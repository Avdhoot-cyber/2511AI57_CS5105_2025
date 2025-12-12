#include <iostream>
#include <vector>
using namespace std;

// Brute force helper to count subsets with given sum
int countSubsetsWithSumBruteHelper(const vector<int>& arr, int n, int sum) {
    if (n == 0) {
        return (sum == 0) ? 1 : 0;
    }
    if (arr[n - 1] > sum) {
        return countSubsetsWithSumBruteHelper(arr, n - 1, sum);
    }
    return countSubsetsWithSumBruteHelper(arr, n - 1, sum) +
           countSubsetsWithSumBruteHelper(arr, n - 1, sum - arr[n - 1]);
}

int countPartitionsBruteForce(const vector<int>& arr, int diff) {
    int total = 0;
    for (int num : arr) total += num;
    if ((total + diff) % 2 != 0) return 0;
    int target = (total + diff) / 2;
    return countSubsetsWithSumBruteHelper(arr, arr.size(), target);
}

// Optimal DP approach (handles zeros as well)
int countPartitionsOptimal(const vector<int>& arr, int diff) {
    int total = 0;
    for (int num : arr) total += num;
    if ((total + diff) % 2 != 0) return 0;
    int target = (total + diff) / 2;

    int n = arr.size();
    vector<vector<int>> dp(n + 1, vector<int>(target + 1, 0));

    for (int i = 0; i <= n; ++i) dp[i][0] = 1;

    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j <= target; ++j) {
            if (arr[i - 1] == 0 && j == 0)
                dp[i][j] = 2 * dp[i - 1][j];
            else if (arr[i - 1] <= j)
                dp[i][j] = dp[i - 1][j] + dp[i - 1][j - arr[i - 1]];
            else
                dp[i][j] = dp[i - 1][j];
        }
    }

    return dp[n][target];
}

int main() {
    cin.sync();

    int n, diff;
    cout << "Enter size of array (N): ";
    cin >> n;
    vector<int> arr(n);
    cout << "Enter array elements:" << endl;
    for (int i = 0; i < n; ++i) cin >> arr[i];
    cout << "Enter difference value (diff): ";
    cin >> diff;

    cout << "\n--- Results ---\n";
    if (n <= 20) {
        cout << "Brute Force: " << countPartitionsBruteForce(arr, diff) << "\n";
    } else {
        cout << "Brute Force: Skipped (input too large)\n";
    }
    cout << "Optimal DP: " << countPartitionsOptimal(arr, diff) << "\n";

    return 0;
}
