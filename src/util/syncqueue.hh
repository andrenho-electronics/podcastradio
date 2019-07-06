#include <memory>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>

template <typename T>
class SyncQueue {
public:
    std::unique_ptr<T> pop()
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        while (queue_.empty()) {
            cond_.wait(mlock);
        }
        auto item = std::move(queue_.front());
        queue_.pop();
        return item;
    }

    template <typename U, typename... Args>
    void push(Args... args)
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        queue_.push(make_unique<U>(args...));
        mlock.unlock();
        cond_.notify_one();
    }
 
    template <typename U>
    void execute(U&& data) {
        while (!queue_.empty()) {
            auto obj = pop();
            obj->execute(data);
        }
    }

private:
    std::queue<std::unique_ptr<T>> queue_;
    std::mutex mutex_;
    std::condition_variable cond_;
    /*
    T pop()
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        while (queue_.empty()) {
            cond_.wait(mlock);
        }
        auto item = move(queue_.front());
        queue_.pop();
        return item;
    }
 
    void pop(T& item)
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        while (queue_.empty()) {
            cond_.wait(mlock);
        }
        item = queue_.front();
        queue_.pop();
    }
 
    void push(const T& item)
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        queue_.push(item);
        mlock.unlock();
        cond_.notify_one();
    }
 
    void push(T&& item)
    {
        std::unique_lock<std::mutex> mlock(mutex_);
        queue_.push(std::move(item));
        mlock.unlock();
        cond_.notify_one();
    }

    template <typename U>
    void execute(U&& data) {
        while (!queue_.empty()) {
            T obj = pop();
            obj->execute(data);
        }
    }
 
private:
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cond_;
    */
};
