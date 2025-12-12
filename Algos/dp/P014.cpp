#include <iostream>
#include <vector>
using namespace std;

// Brute force recursive helper to find subset sum
bool subsetSumBruteHelper(const vector<int>& arr, int n, int sum) {
    if (sum == 0) return true;
    if (n == 0) return false;

    if (arr[n - 1] > sum) 
        return subsetSumBruteHelper(arr, n - 1, sum);

    return subsetSumBruteHelper(arr, n - 1, sum) || 
           subsetSumBruteHelper(arr, n - 1, sum - arr[n - 1]);
}

bool canPartitionBruteForce(const vector<int>& arr) {
    int total = 0;
    for (int num : arr) total += num;
    if (total % 2 != 0) return false;
    return subsetSumBruteHelper(arr, arr.size(), total / 2);
}

// Optimal DP approach
bool canPartitionOptimal(const vector<int>& arr) {
    int n = arr.size();
    int total = 0;
    for (int num : arr) total += num;

    if (total % 2 != 0) return false;
    int target = total / 2;

    vector<vector<bool>> dp(n + 1, vector<bool>(target + 1, false));
    for (int i = 0; i <= n; ++i) dp[i][0] = true;

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= target; ++j) {
            if (arr[i - 1] > j)
                dp[i][j] = dp[i - 1][j];
            else
                dp[i][j] = dp[i - 1][j] || dp[i - 1][j - arr[i - 1]];
        }
    }
    return dp[n][target];
}

// Main function with user input
int main() {
    int n;
    cout << "Enter size of array (N): ";
    cin >> n;
    vector<int> arr(n);
    cout << "Enter array elements:" << endl;
    for (int i = 0; i < n; ++i) cin >> arr[i];

    cout << "\n--- Results ---" << endl;
    if (n <= 20) {
        cout << "Brute Force: " << (canPartitionBruteForce(arr) ? "True" : "False") << endl;
    } else {
        cout << "Brute Force: Skipped (large input size)" << endl;
    }
    cout << "Optimal DP: " << (canPartitionOptimal(arr) ? "True" : "False") << endl;

    return 0;
}