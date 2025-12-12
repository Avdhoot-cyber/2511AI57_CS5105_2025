#include <iostream>
#include <vector>
using namespace std;

// Brute force recursive helper
int countTargetSumWaysBruteHelper(const vector<int>& arr, int index, int currentSum, int target) {
    if (index == arr.size()) {
        return (currentSum == target) ? 1 : 0;
    }
    int add = countTargetSumWaysBruteHelper(arr, index + 1, currentSum + arr[index], target);
    int subtract = countTargetSumWaysBruteHelper(arr, index + 1, currentSum - arr[index], target);
    return add + subtract;
}

int countTargetSumWaysBruteForce(const vector<int>& arr, int target) {
    return countTargetSumWaysBruteHelper(arr, 0, 0, target);
}

// Count subsets with given sum (used for optimal solution)
int countSubsetsWithSum(const vector<int>& arr, int sum) {
    int n = arr.size();
    vector<vector<int>> dp(n + 1, vector<int>(sum + 1, 0));

    for (int i = 0; i <= n; ++i) dp[i][0] = 1;  // sum=0 possible with empty subset

    for (int i = 1; i <= n; ++i) {
        for (int j = 0; j <= sum; ++j) {
            if (arr[i - 1] > j)
                dp[i][j] = dp[i - 1][j];
            else
                dp[i][j] = dp[i - 1][j] + dp[i - 1][j - arr[i - 1]];
        }
    }
    return dp[n][sum];
}

// Optimal approach using subset sum count
int countTargetSumWaysOptimal(const vector<int>& arr, int target) {
    int total = 0;
    for (int num : arr) total += num;

    // target = (S1 - S2), total = S1 + S2
    // => S1 = (total + target)/2
    if ((total + target) % 2 != 0) return 0;
    int subsetSum = (total + target) / 2;
    if (subsetSum < 0) return 0;

    return countSubsetsWithSum(arr, subsetSum);
}

// Main function with user input
int main() {
    cin.sync();

    int n, target;
    cout << "Enter size of array (N): ";
    cin >> n;
    vector<int> arr(n);
    cout << "Enter array elements:" << endl;
    for (int i = 0; i < n; ++i) cin >> arr[i];
    cout << "Enter target value: ";
    cin >> target;

    cout << "\n--- Results ---" << endl;
    if (n <= 20) {
        cout << "Brute Force: " << countTargetSumWaysBruteForce(arr, target) << endl;
    } else {
        cout << "Brute Force: Skipped (input too large)" << endl;
    }
    cout << "Optimal DP: " << countTargetSumWaysOptimal(arr, target) << endl;

    return 0;
}