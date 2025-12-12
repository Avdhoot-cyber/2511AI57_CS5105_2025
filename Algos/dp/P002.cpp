#include <bits/stdc++.h>
using namespace std;

// -------------------------
// Memoization Approach
// -------------------------
int solveMemo(int idx, vector<int>& height, vector<int>& dp) {
    if (idx == 0) return 0;
    if (dp[idx] != -1) return dp[idx];

    int oneStep = solveMemo(idx - 1, height, dp) + abs(height[idx] - height[idx - 1]);
    int twoStep = INT_MAX;
    if (idx > 1)
        twoStep = solveMemo(idx - 2, height, dp) + abs(height[idx] - height[idx - 2]);

    return dp[idx] = min(oneStep, twoStep);
}

int frogJumpMemo(vector<int>& height) {
    int n = height.size();
    vector<int> dp(n, -1);
    return solveMemo(n - 1, height, dp);
}

// -------------------------
// Tabulation + Space Optimized Approach
// -------------------------
int frogJumpOptimal(vector<int>& height) {
    int n = height.size();
    int prev = 0, prev2 = 0;

    for (int i = 1; i < n; i++) {
        int oneStep = prev + abs(height[i] - height[i - 1]);
        int twoStep = INT_MAX;
        if (i > 1) twoStep = prev2 + abs(height[i] - height[i - 2]);

        int curr = min(oneStep, twoStep);
        prev2 = prev;
        prev = curr;
    }
    return prev;
}

// -------------------------
// Driver Code
// -------------------------
int main() {
    int n;
    cout << "Enter number of stairs: ";
    cin >> n;

    vector<int> height(n);
    cout << "Enter heights: ";
    for (int i = 0; i < n; i++) cin >> height[i];

    cout << "Minimum Energy (Memoization): " << frogJumpMemo(height) << endl;
    cout << "Minimum Energy (Optimal): " << frogJumpOptimal(height) << endl;

    return 0;
}