/**
 * @file PerformanceTimer.h
 * @brief Performance profiling utility
 */

#pragma once

#include <chrono>
#include <string>
#include <iostream>

namespace Utils {

/**
 * @class PerformanceTimer
 * @brief RAII-based performance timer for profiling
 */
class PerformanceTimer {
public:
    /**
     * @brief Constructor - starts the timer
     * @param name Name of the operation being timed
     * @param verbose If true, prints timing on destruction
     */
    explicit PerformanceTimer(const std::string& name = "", bool verbose = true)
        : name(name)
        , verbose(verbose)
        , start(std::chrono::high_resolution_clock::now())
    {
    }
    
    /**
     * @brief Destructor - prints elapsed time if verbose
     */
    ~PerformanceTimer()
    {
        if (verbose) {
            auto elapsed = getElapsedMs();
            std::cout << "[Timer] " << name << ": " << elapsed << " ms" << std::endl;
        }
    }
    
    /**
     * @brief Get elapsed time in milliseconds
     * @return Elapsed time in ms
     */
    double getElapsedMs() const
    {
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        return duration.count() / 1000.0;
    }
    
    /**
     * @brief Get elapsed time in seconds
     * @return Elapsed time in seconds
     */
    double getElapsedSeconds() const
    {
        return getElapsedMs() / 1000.0;
    }
    
    /**
     * @brief Reset the timer
     */
    void reset()
    {
        start = std::chrono::high_resolution_clock::now();
    }

private:
    std::string name;
    bool verbose;
    std::chrono::high_resolution_clock::time_point start;
};

} // namespace Utils
