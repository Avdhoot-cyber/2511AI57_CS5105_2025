#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>

using namespace std;

// --- Brute Force Approach (Exponential Time) ---

int max_non_adjacent_sum_bruteforce(int index, const vector<int>& arr, int N) {
    // Base Case 1: If the index is out of bounds, the sum is 0
    if (index >= N) {
        return 0;
    }

    // Choice 1: Include the current element arr[index]
    // Must skip arr[index + 1], so move to index + 2
    int pick = arr[index] + max_non_adjacent_sum_bruteforce(index + 2, arr, N);

    // Choice 2: Exclude the current element arr[index]
    // Move to the next element, index + 1
    int not_pick = max_non_adjacent_sum_bruteforce(index + 1, arr, N);

    // Return the maximum of the two choices
    return max(pick, not_pick);
}

// --- Optimal Approach (Memoization - Top-Down DP) ---


int max_non_adjacent_sum_optimal(int index, const vector<int>& arr, int N, vector<int>& dp) {
    // Base Case 1: If the index is out of bounds, the sum is 0
    if (index >= N) {
        return 0;
    }

    // Check DP: If the result is already computed, return it
    if (dp[index] != -1) {
        return dp[index];
    }

    // Choice 1: Include the current element arr[index]
    // Must skip arr[index + 1], so move to index + 2
    int pick = arr[index] + max_non_adjacent_sum_optimal(index + 2, arr, N, dp);

    // Choice 2: Exclude the current element arr[index]
    // Move to the next element, index + 1
    int not_pick = max_non_adjacent_sum_optimal(index + 1, arr, N, dp);

    // Store the computed result in the DP table before returning
    return dp[index] = max(pick, not_pick);
}

int main() {
    int N;

    // 1. Get total number of elements (N)
    cout << "Enter the total number of elements (N): ";
    if (!(cin >> N) || N <= 0) {
        cerr << "Invalid input for N. Exiting." << endl;
        return 1;
    }

    // 2. Get the elements
    vector<int> arr(N);
    cout << "Enter the " << N << " positive integers, separated by spaces:" << endl;
    for (int i = 0; i < N; ++i) {
        if (!(cin >> arr[i]) || arr[i] <= 0) {
            cerr << "Invalid input: Please enter positive integers only. Exiting." << endl;
            return 1;
        }
    }

    cout << "\n--- Problem Setup ---" << endl;
    cout << "Total Elements (N): " << N << endl;
    cout << "Array: ";
    for (int x : arr) {
        cout << x << " ";
    }
    cout << endl;

    // --- Brute Force Execution (O(2^N)) ---
    int bf_result = max_non_adjacent_sum_bruteforce(0, arr, N);
    cout << "\n--- Brute Force Result ---" << endl;
    cout << "Maximum non-adjacent sum: " << bf_result << endl;

    // --- Optimal (Memoization) Execution (O(N)) ---
    vector<int> dp(N, -1); // DP array initialized with -1
    int optimal_result = max_non_adjacent_sum_optimal(0, arr, N, dp);
    cout << "\n--- Optimal (DP) Result ---" << endl;
    cout << "Maximum non-adjacent sum: " << optimal_result << endl;
    
    return 0;
}