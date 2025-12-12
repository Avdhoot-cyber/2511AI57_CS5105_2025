#include <iostream>
#include <vector>
using namespace std;

// Brute force approach: recursive
int countWaysBrute(int n, int current=0) {
    if (current == n) return 1;
    if (current > n) return 0;
    return countWaysBrute(n, current + 1) + countWaysBrute(n, current + 2);
}

// Optimal approach: using DP
int countWaysOptimal(int n) {
    if (n == 0 || n == 1) return 1;
    vector<int> dp(n + 1, 0);
    dp[0] = 1;
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i-1] + dp[i-2];
    }
    return dp[n];
}

int main() {
    int n = 5; // Example input
    cout << "Brute force ways: " << countWaysBrute(n) << endl;
    cout << "Optimal ways: " << countWaysOptimal(n) << endl;
    return 0;
}