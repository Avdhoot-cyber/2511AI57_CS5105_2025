#include <iostream>
#include <vector>
using namespace std;

// Brute force recursive helper
bool subsetSumBruteHelper(const vector<int>& arr, int n, int sum) {
    if (sum == 0) return true;
    if (n == 0) return false;

    if (arr[n - 1] > sum)
        return subsetSumBruteHelper(arr, n - 1, sum);

    return subsetSumBruteHelper(arr, n - 1, sum) || 
           subsetSumBruteHelper(arr, n - 1, sum - arr[n - 1]);
}

bool subsetSumBruteForce(const vector<int>& arr, int sum) {
    return subsetSumBruteHelper(arr, arr.size(), sum);
}

// Optimal DP approach
bool subsetSumOptimal(const vector<int>& arr, int sum) {
    int n = arr.size();
    vector<vector<bool>> dp(n + 1, vector<bool>(sum + 1, false));

    // Initialize dp[i][0] = true
    for (int i = 0; i <= n; ++i) dp[i][0] = true;

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= sum; ++j) {
            if (arr[i - 1] > j)
                dp[i][j] = dp[i - 1][j];
            else
                dp[i][j] = dp[i - 1][j] || dp[i - 1][j - arr[i - 1]];
        }
    }

    return dp[n][sum];
}

// Main function with user input
int main() {
    int n, k;
    cout << "Enter size of array (N): ";
    cin >> n;
    cout << "Enter array elements:" << endl;
    vector<int> arr(n);
    for (int i = 0; i < n; ++i) cin >> arr[i];
    cout << "Enter sum value (K): ";
    cin >> k;

    cout << "\n--- Results ---" << endl;
    if (n <= 20) {
        cout << "Brute Force: " << (subsetSumBruteForce(arr, k) ? "True" : "False") << endl;
    } else {
        cout << "Brute Force: Skipped (large input size)" << endl;
    }
    cout << "Optimal DP: " << (subsetSumOptimal(arr, k) ? "True" : "False") << endl;

    return 0;
}