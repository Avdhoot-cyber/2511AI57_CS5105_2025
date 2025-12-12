#include <iostream>
#include <climits>
#include <vector>
#include <algorithm>
using namespace std;

// Brute force helper: track sums of two subsets recursively
void bruteHelper(const vector<int>& arr, int index, int sum1, int sum2, int &minDiff) {
    if (index == arr.size()) {
        minDiff = min(minDiff, abs(sum1 - sum2));
        return;
    }
    // Include current element in subset1
    bruteHelper(arr, index + 1, sum1 + arr[index], sum2, minDiff);
    // Include current element in subset2
    bruteHelper(arr, index + 1, sum1, sum2 + arr[index], minDiff);
}

int minSubsetSumDiffBruteForce(const vector<int>& arr ) {
    int minDiff = INT_MAX;
    bruteHelper(arr, 0, 0, 0, minDiff);
    return minDiff;
}

// Optimal DP approach
int minSubsetSumDiffOptimal(const vector<int>& arr) {
    int total = 0;
    for (int num : arr) total += num;

    int n = arr.size();
    int half = total / 2;
    vector<vector<bool>> dp(n + 1, vector<bool>(half + 1, false));

    for (int i = 0; i <= n; ++i) dp[i][0] = true;

    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= half; ++j) {
            if (arr[i - 1] <= j)
                dp[i][j] = dp[i - 1][j] || dp[i - 1][j - arr[i - 1]];
            else
                dp[i][j] = dp[i - 1][j];
        }
    }

    int minDiff = INT_MAX;
    for (int j = half; j >= 0; --j) {
        if (dp[n][j]) {
            minDiff = total - 2 * j;
            break;
        }
    }
    return minDiff;
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
        cout << "Brute Force: " << minSubsetSumDiffBruteForce(arr) << endl;
    } else {
        cout << "Brute Force: Skipped (large input size)" << endl;
    }
    cout << "Optimal DP: " << minSubsetSumDiffOptimal(arr) << endl;

    return 0;
}