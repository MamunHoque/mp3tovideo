/**
 * @file ThreadPool.cpp
 * @brief Implementation of ThreadPool class
 */

#include "utils/ThreadPool.h"

namespace Utils {

ThreadPool::ThreadPool(size_t numThreads)
    : stop(false), activeTasks(0)
{
    if (numThreads == 0) {
        numThreads = std::thread::hardware_concurrency();
        if (numThreads == 0) numThreads = 4; // Fallback
    }
    
    workers.reserve(numThreads);
    
    for(size_t i = 0; i < numThreads; ++i) {
        workers.emplace_back([this] {
            while(true) {
                std::function<void()> task;
                
                {
                    std::unique_lock<std::mutex> lock(this->queueMutex);
                    this->condition.wait(lock, [this] { 
                        return this->stop || !this->tasks.empty(); 
                    });
                    
                    if(this->stop && this->tasks.empty())
                        return;
                    
                    task = std::move(this->tasks.front());
                    this->tasks.pop();
                }
                
                task();
            }
        });
    }
}

ThreadPool::~ThreadPool()
{
    {
        std::unique_lock<std::mutex> lock(queueMutex);
        stop = true;
    }
    
    condition.notify_all();
    
    for(std::thread &worker: workers)
        worker.join();
}

void ThreadPool::wait()
{
    std::unique_lock<std::mutex> lock(queueMutex);
    waitCondition.wait(lock, [this] { 
        return tasks.empty() && activeTasks == 0; 
    });
}

} // namespace Utils
