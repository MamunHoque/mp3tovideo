/**
 * @file ThreadPool.h
 * @brief High-performance thread pool for parallel frame generation
 */

#pragma once

#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <future>
#include <memory>
#include <stdexcept>

namespace Utils {

/**
 * @class ThreadPool
 * @brief Thread pool implementation for efficient parallel task execution
 */
class ThreadPool {
public:
    /**
     * @brief Constructor - creates thread pool with specified number of threads
     * @param numThreads Number of worker threads (0 = hardware concurrency)
     */
    explicit ThreadPool(size_t numThreads = 0);
    
    /**
     * @brief Destructor - waits for all tasks to complete
     */
    ~ThreadPool();
    
    /**
     * @brief Enqueue a task for execution
     * @tparam F Function type
     * @tparam Args Argument types
     * @param f Function to execute
     * @param args Arguments to pass to function
     * @return Future for the result
     */
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... args) 
        -> std::future<typename std::invoke_result<F, Args...>::type>;
    
    /**
     * @brief Get number of worker threads
     * @return Number of threads in pool
     */
    size_t size() const { return workers.size(); }
    
    /**
     * @brief Wait for all tasks to complete
     */
    void wait();

private:
    // Worker threads
    std::vector<std::thread> workers;
    
    // Task queue
    std::queue<std::function<void()>> tasks;
    
    // Synchronization
    std::mutex queueMutex;
    std::condition_variable condition;
    std::condition_variable waitCondition;
    
    // State
    bool stop;
    size_t activeTasks;
};

// Template implementation
template<class F, class... Args>
auto ThreadPool::enqueue(F&& f, Args&&... args) 
    -> std::future<typename std::invoke_result<F, Args...>::type>
{
    using return_type = typename std::invoke_result<F, Args...>::type;

    auto task = std::make_shared<std::packaged_task<return_type()>>(
        std::bind(std::forward<F>(f), std::forward<Args>(args)...)
    );
        
    std::future<return_type> res = task->get_future();
    {
        std::unique_lock<std::mutex> lock(queueMutex);

        if(stop)
            throw std::runtime_error("enqueue on stopped ThreadPool");

        tasks.emplace([task, this]() { 
            ++activeTasks;
            (*task)(); 
            --activeTasks;
            waitCondition.notify_all();
        });
    }
    condition.notify_one();
    return res;
}

} // namespace Utils
