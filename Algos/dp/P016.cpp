#include <iostream>
#include <vector>
#include <climits>
using namespace std;

// Brute force recursive helper
int countSubsetsBruteHelper(const vector<int>& arr, int index, int sum) {
    if (sum == 0) return 1;
    if (index == 0) return 0;

    // Exclude current element
    int exclude = countSubsetsBruteHelper(arr, index - 1, sum);

    // Include current element if possible
    int include = 0;
    if (arr[index - 1] <= sum)
        include = countSubsetsBruteHelper(arr, index - 1, sum - arr[index - 1]);

    return exclude + include;
}

int countSubsetsBruteForce(const vector<int>& arr, int sum) {
    return countSubsetsBruteHelper(arr, arr.size(), sum);
}

// Optimal DP approach
int countSubsetsOptimal(const vector<int>& arr, int sum) {
    int n = arr.size();
    vector<vector<int>> dp(n + 1, vector<int>(sum + 1, 0));

    // Initialize: dp[i][0] = 1 for all i
    for (int i = 0; i <= n; ++i) dp[i][0] = 1;

    // Fill DP table
    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j <= sum; ++j) {
            // Exclude current element
            dp[i][j] = dp[i - 1][j];

            // Include current element if possible
            if (arr[i - 1] <= j)
                dp[i][j] += dp[i - 1][j - arr[i - 1]];
        }
    }

    return dp[n][sum];
}

// Main function with user input
int main() {
    int n, k;
    cout << "Enter size of array (N): ";
    cin >> n;

    vector<int> arr(n);
    cout << "Enter array elements:" << endl;
    for (int i = 0; i < n; ++i) cin >> arr[i];

    cout << "Enter target sum (K): ";
    cin >> k;

    cout << "\n--- Results ---" << endl;
    if (n <= 20) {
        cout << "Brute Force: " << countSubsetsBruteForce(arr, k) << endl;
    } else {
        cout << "Brute Force: Skipped (input too large)" << endl;
    }
    cout << "Optimal DP: " << countSubsetsOptimal(arr, k) << endl;

    return 0;
}