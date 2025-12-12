#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <string> // Added for std::to_string

using namespace std;

// Define a large number for initialization (simulating infinity)
// Using INT_MAX / 2 to prevent overflow when adding costs
const int INF = numeric_limits<int>::max() / 2;

// --- Brute Force Approach (Exponential Time) ---

/**
 * @brief Computes the minimum cost to reach the last stone (N-1) starting from the current stone (index).
 *
 * This function explores all possible jump sequences recursively, leading to a high time complexity.
 *
 * @param index The current stone index (0 to N-1).
 * @param heights The vector of stone heights.
 * @param K The maximum number of steps the frog can jump.
 * @param N The total number of stones.
 * @return The minimum total energy cost to reach the last stone.
 */
int min_cost_bruteforce(int index, const vector<int>& heights, int K, int N) {
    // Base Case: We are at the final stone, no more cost
    if (index == N - 1) {
        return 0;
    }

    int min_total_cost = INF;

    // Iterate through all possible jump lengths from 1 up to K
    for (int j = 1; j <= K; ++j) {
        int next_index = index + j;

        // Check if the jump leads to a valid stone within the array bounds
        if (next_index < N) {
            // Cost of the current jump
            int jump_cost = abs(heights[index] - heights[next_index]);

            // Recursively find the minimum cost from the next stone
            int remaining_cost = min_cost_bruteforce(next_index, heights, K, N);

            // Note: We use remaining_cost != INF to prevent integer overflow when adding
            // Also, INF was halved to prevent overflow if added to another cost.
            if (remaining_cost != INF) {
                // Update the minimum total cost
                int current_path_cost = jump_cost + remaining_cost;
                min_total_cost = min(min_total_cost, current_path_cost);
            }
        }
    }

    return min_total_cost;
}

// --- Optimal Approach (Memoization - Top-Down DP) ---

/**
 * @brief Computes the minimum cost to reach the last stone using memoization (Dynamic Programming).
 *
 * This function optimizes the recursive calls by storing and reusing results for overlapping subproblems.
 * Time Complexity: O(N * K).
 *
 * @param index The current stone index (0 to N-1).
 * @param heights The vector of stone heights.
 * @param K The maximum number of steps the frog can jump.
 * @param N The total number of stones.
 * @param dp The memoization table (vector<int> initialized to -1).
 * @return The minimum total energy cost to reach the last stone.
 */
int min_cost_optimal(int index, const vector<int>& heights, int K, int N, vector<int>& dp) {
    // Base Case
    if (index == N - 1) {
        return 0;
    }

    // Check DP: If the result is already computed, return it
    if (dp[index] != -1) {
        return dp[index];
    }

    int min_total_cost = INF;

    // Explore Jumps: Iterate through all possible jump lengths from 1 up to K
    for (int j = 1; j <= K; ++j) {
        int next_index = index + j;

        // Check if the jump leads to a valid stone
        if (next_index < N) {
            // Cost of the current jump
            int jump_cost = abs(heights[index] - heights[next_index]);

            // Recursively find the minimum cost from the next stone (will use memoized values)
            int remaining_cost = min_cost_optimal(next_index, heights, K, N, dp);

            if (remaining_cost != INF) {
                // Update the minimum total cost
                int current_path_cost = jump_cost + remaining_cost;
                min_total_cost = min(min_total_cost, current_path_cost);
            }
        }
    }

    // Store the computed result in the DP table before returning
    return dp[index] = min_total_cost;
}

int main() {
    int N;
    int K;

    // 1. Get total number of stones (N)
    cout << "Enter the total number of stones (N): ";
    if (!(cin >> N) || N <= 0) {
        cerr << "Invalid input for N. Exiting." << endl;
        return 1;
    }

    // 2. Get maximum jump limit (K)
    cout << "Enter the maximum jump limit (K): ";
    if (!(cin >> K) || K <= 0) {
        cerr << "Invalid input for K. Exiting." << endl;
        return 1;
    }

    // 3. Get the heights
    vector<int> heights(N);
    cout << "Enter the heights of the " << N << " stones, separated by spaces:" << endl;
    for (int i = 0; i < N; ++i) {
        if (!(cin >> heights[i])) {
            cerr << "Invalid height input at stone " << i + 1 << ". Exiting." << endl;
            return 1;
        }
    }

    cout << "\n--- Problem Setup ---" << endl;
    cout << "Total Stones (N): " << N << endl;
    cout << "Max Jump (K): " << K << endl;
    cout << "Heights: ";
    for (int h : heights) {
        cout << h << " ";
    }
    cout << endl;

    // --- Brute Force Execution ---
    // Note: This function may take a very long time for large N and K.
    int bf_result = min_cost_bruteforce(0, heights, K, N);
    cout << "\n--- Brute Force Result (O(K^N)) ---" << endl;
    // Check if the result is valid
    if (bf_result == INF) {
        cout << "Minimum cost: Impossible to reach the end." << endl;
    } else {
        cout << "Minimum cost: " << bf_result << endl;
    }

    // --- Optimal (Memoization) Execution ---
    vector<int> dp(N, -1); // DP array initialized with -1
    int optimal_result = min_cost_optimal(0, heights, K, N, dp);
    cout << "\n--- Optimal (DP) Result (O(N*K)) ---" << endl;
    // Check if the result is valid
    if (optimal_result == INF) {
        cout << "Minimum cost: Impossible to reach the end." << endl;
    } else {
        cout << "Minimum cost: " << optimal_result << endl;
    }
    
    return 0;
}