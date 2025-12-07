/**
 * @file AudioProcessor.cpp
 * @brief Implementation of audio processing with FFTW3
 */

#include "audio/AudioProcessor.h"
#include <sndfile.h>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <stdexcept>

namespace Audio {

AudioProcessor::AudioProcessor(const std::string& audioPath)
    : audioPath(audioPath)
    , sampleRate(0)
    , duration(0.0)
    , nFft(2048)
    , frameRate(30)
    , fftwPlan(nullptr)
    , fftwIn(nullptr)
    , fftwOut(nullptr)
    , numBands(64)
{
}

AudioProcessor::~AudioProcessor() {
    cleanup();
}

AudioProcessor::AudioProcessor(AudioProcessor&& other) noexcept
    : audioPath(std::move(other.audioPath))
    , audioData(std::move(other.audioData))
    , sampleRate(other.sampleRate)
    , duration(other.duration)
    , nFft(other.nFft)
    , frameRate(other.frameRate)
    , fftwPlan(other.fftwPlan)
    , fftwIn(other.fftwIn)
    , fftwOut(other.fftwOut)
    , spectrumCache(std::move(other.spectrumCache))
    , bandsCache(std::move(other.bandsCache))
    , numBands(other.numBands)
{
    other.fftwPlan = nullptr;
    other.fftwIn = nullptr;
    other.fftwOut = nullptr;
}

AudioProcessor& AudioProcessor::operator=(AudioProcessor&& other) noexcept {
    if (this != &other) {
        cleanup();
        
        audioPath = std::move(other.audioPath);
        audioData = std::move(other.audioData);
        sampleRate = other.sampleRate;
        duration = other.duration;
        nFft = other.nFft;
        frameRate = other.frameRate;
        fftwPlan = other.fftwPlan;
        fftwIn = other.fftwIn;
        fftwOut = other.fftwOut;
        spectrumCache = std::move(other.spectrumCache);
        bandsCache = std::move(other.bandsCache);
        numBands = other.numBands;
        
        other.fftwPlan = nullptr;
        other.fftwIn = nullptr;
        other.fftwOut = nullptr;
    }
    return *this;
}

bool AudioProcessor::loadAudio() {
    SF_INFO sfInfo;
    SNDFILE* file = sf_open(audioPath.c_str(), SFM_READ, &sfInfo);
    
    if (!file) {
        std::cerr << "Error opening audio file: " << audioPath << std::endl;
        std::cerr << "libsndfile error: " << sf_strerror(nullptr) << std::endl;
        return false;
    }
    
    sampleRate = sfInfo.samplerate;
    duration = static_cast<double>(sfInfo.frames) / sampleRate;
    
    // Read audio data
    std::vector<float> tempData(sfInfo.frames * sfInfo.channels);
    sf_count_t readCount = sf_readf_float(file, tempData.data(), sfInfo.frames);
    
    if (readCount != sfInfo.frames) {
        std::cerr << "Error reading audio data" << std::endl;
        sf_close(file);
        return false;
    }
    
    // Convert to mono if stereo
    audioData.resize(sfInfo.frames);
    if (sfInfo.channels == 1) {
        audioData = std::move(tempData);
    } else {
        for (sf_count_t i = 0; i < sfInfo.frames; ++i) {
            float sum = 0.0f;
            for (int ch = 0; ch < sfInfo.channels; ++ch) {
                sum += tempData[i * sfInfo.channels + ch];
            }
            audioData[i] = sum / sfInfo.channels;
        }
    }
    
    sf_close(file);
    
    std::cout << "Loaded audio: " << duration << "s, " << sampleRate << "Hz" << std::endl;
    return true;
}

bool AudioProcessor::computeSpectrum(int frameRate, int nFft) {
    if (audioData.empty()) {
        std::cerr << "No audio data loaded" << std::endl;
        return false;
    }
    
    this->frameRate = frameRate;
    this->nFft = nFft;
    
    // Allocate FFTW arrays
    fftwIn = fftw_alloc_real(nFft);
    fftwOut = fftw_alloc_complex(nFft / 2 + 1);
    fftwPlan = fftw_plan_dft_r2c_1d(nFft, fftwIn, fftwOut, FFTW_ESTIMATE);
    
    if (!fftwPlan) {
        std::cerr << "Failed to create FFTW plan" << std::endl;
        return false;
    }
    
    // Calculate number of frames
    int totalFrames = static_cast<int>(duration * frameRate);
    int samplesPerFrame = sampleRate / frameRate;
    
    spectrumCache.clear();
    spectrumCache.reserve(totalFrames);
    
    // Hanning window
    std::vector<double> window(nFft);
    for (int i = 0; i < nFft; ++i) {
        window[i] = 0.5 * (1.0 - std::cos(2.0 * M_PI * i / (nFft - 1)));
    }
    
    // Process each frame
    for (int frame = 0; frame < totalFrames; ++frame) {
        int startSample = frame * samplesPerFrame;
        int endSample = std::min(startSample + nFft, static_cast<int>(audioData.size()));
        
        // Fill FFT input with windowed audio data
        std::fill(fftwIn, fftwIn + nFft, 0.0);
        for (int i = 0; i < std::min(nFft, endSample - startSample); ++i) {
            fftwIn[i] = audioData[startSample + i] * window[i];
        }
        
        // Execute FFT
        fftw_execute(fftwPlan);
        
        // Calculate magnitudes
        std::vector<float> magnitudes(nFft / 2);
        for (int i = 0; i < nFft / 2; ++i) {
            double real = fftwOut[i][0];
            double imag = fftwOut[i][1];
            magnitudes[i] = static_cast<float>(std::sqrt(real * real + imag * imag));
        }
        
        spectrumCache.push_back(std::move(magnitudes));
    }
    
    std::cout << "Computed spectrum for " << totalFrames << " frames" << std::endl;
    return true;
}

bool AudioProcessor::getFrequencyBands(int numBands, int frameRate) {
    if (spectrumCache.empty()) {
        if (!computeSpectrum(frameRate)) {
            return false;
        }
    }
    
    this->numBands = numBands;
    int spectrumSize = spectrumCache[0].size();
    
    bandsCache.clear();
    bandsCache.reserve(spectrumCache.size());
    
    // Create logarithmic frequency bands
    std::vector<int> bandLimits(numBands + 1);
    double logMin = std::log10(1.0);
    double logMax = std::log10(spectrumSize);
    double logStep = (logMax - logMin) / numBands;
    
    for (int i = 0; i <= numBands; ++i) {
        bandLimits[i] = static_cast<int>(std::pow(10.0, logMin + i * logStep));
    }
    
    // Average spectrum into bands
    for (const auto& spectrum : spectrumCache) {
        std::vector<float> bands(numBands);
        
        for (int band = 0; band < numBands; ++band) {
            int start = bandLimits[band];
            int end = bandLimits[band + 1];
            
            float sum = 0.0f;
            int count = 0;
            for (int i = start; i < end && i < spectrumSize; ++i) {
                sum += spectrum[i];
                count++;
            }
            
            bands[band] = count > 0 ? sum / count : 0.0f;
        }
        
        // Normalize bands
        float maxVal = *std::max_element(bands.begin(), bands.end());
        if (maxVal > 0.0f) {
            for (auto& val : bands) {
                val /= maxVal;
            }
        }
        
        bandsCache.push_back(std::move(bands));
    }
    
    std::cout << "Created " << numBands << " frequency bands" << std::endl;
    return true;
}

std::vector<float> AudioProcessor::getFrameSpectrum(int frameNumber) const {
    if (frameNumber < 0 || frameNumber >= static_cast<int>(spectrumCache.size())) {
        return {};
    }
    return spectrumCache[frameNumber];
}

std::vector<float> AudioProcessor::getFrameBands(int frameNumber) const {
    if (frameNumber < 0 || frameNumber >= static_cast<int>(bandsCache.size())) {
        return {};
    }
    return bandsCache[frameNumber];
}

float AudioProcessor::getAudioIntensity(int frameNumber, int frameRate, int windowSize) const {
    if (audioData.empty() || frameNumber < 0) {
        return 0.0f;
    }
    
    int samplesPerFrame = sampleRate / frameRate;
    int startSample = frameNumber * samplesPerFrame;
    int endSample = std::min(startSample + samplesPerFrame * windowSize, 
                            static_cast<int>(audioData.size()));
    
    if (startSample >= static_cast<int>(audioData.size())) {
        return 0.0f;
    }
    
    // Calculate RMS
    double sum = 0.0;
    int count = 0;
    for (int i = startSample; i < endSample; ++i) {
        sum += audioData[i] * audioData[i];
        count++;
    }
    
    float rms = count > 0 ? std::sqrt(sum / count) : 0.0f;
    return std::min(rms * 10.0f, 1.0f); // Scale and clamp
}

void AudioProcessor::cleanup() {
    if (fftwPlan) {
        fftw_destroy_plan(fftwPlan);
        fftwPlan = nullptr;
    }
    if (fftwIn) {
        fftw_free(fftwIn);
        fftwIn = nullptr;
    }
    if (fftwOut) {
        fftw_free(fftwOut);
        fftwOut = nullptr;
    }
}

} // namespace Audio
