#ifndef PERFORMANCE_PROFILER_H
#define PERFORMANCE_PROFILER_H

#include <chrono>
#include <string>
#include <unordered_map>
#include <iostream>

/**
 * C++性能分析器
 * 用于监控RAG系统各模块的性能指标
 */

class PerformanceProfiler {
public:
    struct ProfileData {
        std::chrono::high_resolution_clock::time_point start_time;
        std::chrono::duration<double> total_time{0};
        size_t call_count = 0;
        
        double average_time() const {
            return call_count > 0 ? total_time.count() / call_count : 0.0;
        }
    };
    
private:
    std::unordered_map<std::string, ProfileData> profiles;
    
public:
    void start_timing(const std::string& name) {
        profiles[name].start_time = std::chrono::high_resolution_clock::now();
    }
    
    void end_timing(const std::string& name) {
        auto end_time = std::chrono::high_resolution_clock::now();
        auto& profile = profiles[name];
        
        auto duration = end_time - profile.start_time;
        profile.total_time += duration;
        profile.call_count++;
    }
    
    void print_report() const {
        std::cout << "\n=== Performance Report ===" << std::endl;
        std::cout << "Function Name\t\tCalls\tTotal(s)\tAvg(ms)" << std::endl;
        std::cout << "------------------------------------------------" << std::endl;
        
        for (const auto& [name, data] : profiles) {
            std::cout << name << "\t\t" 
                     << data.call_count << "\t"
                     << data.total_time.count() << "\t"
                     << data.average_time() * 1000 << std::endl;
        }
    }
    
    double get_total_time(const std::string& name) const {
        auto it = profiles.find(name);
        return it != profiles.end() ? it->second.total_time.count() : 0.0;
    }
    
    size_t get_call_count(const std::string& name) const {
        auto it = profiles.find(name);
        return it != profiles.end() ? it->second.call_count : 0;
    }
};

// RAII计时器类
class ScopedTimer {
private:
    PerformanceProfiler& profiler;
    std::string name;
    
public:
    ScopedTimer(PerformanceProfiler& p, const std::string& n) 
        : profiler(p), name(n) {
        profiler.start_timing(name);
    }
    
    ~ScopedTimer() {
        profiler.end_timing(name);
    }
};

// 便利宏定义
#define PROFILE_SCOPE(profiler, name) ScopedTimer timer(profiler, name)
#define PROFILE_FUNCTION(profiler) ScopedTimer timer(profiler, __FUNCTION__)

#endif // PERFORMANCE_PROFILER_H