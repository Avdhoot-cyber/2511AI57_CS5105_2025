#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// Brute-force recursive approach
int bruteHelper(int i, int j, int m, int n) {
    // Base case: reached destination
    if (i == m - 1 && j == n - 1) return 1;
    
    // Out of bounds
    if (i >= m || j >= n) return 0;
    
    // Move down + move right
    return bruteHelper(i + 1, j, m, n) + bruteHelper(i, j + 1, m, n);
}

int uniquePathsBruteForce(int m, int n) {
    return bruteHelper(0, 0, m, n);
}

// Optimal DP approach (2D array)
int uniquePathsOptimal(int m, int n) {
    vector<vector<int>> dp(m, vector<int>(n, 1));
    
    for (int i = 1; i < m; ++i) {
        for (int j = 1; j < n; ++j) {
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
        }
    }
    
    return dp[m - 1][n - 1];
}

// Optimal DP approach (Space Optimized - 1D array)
int uniquePathsOptimized(int m, int n) {
    vector<int> dp(n, 1);
    
    for (int i = 1; i < m; ++i) {
        for (int j = 1; j < n; ++j) {
            dp[j] = dp[j] + dp[j - 1];
        }
    }
    
    return dp[n - 1];
}

// Main function with user input
int main() {
    int m, n;
    cout << "Enter the number of rows (M): ";
    cin >> m;
    cout << "Enter the number of columns (N): ";
    cin >> n;
    
    cout << "\n--- Results ---" << endl;
    
    // Note: Brute force can be very slow for larger inputs
    if (m <= 10 && n <= 10) {
        cout << "Brute Force: " << uniquePathsBruteForce(m, n) << endl;
    } else {
        cout << "Brute Force: Skipped (too large, would take too long)" << endl;
    }
    
    cout << "Optimal DP (2D): " << uniquePathsOptimal(m, n) << endl;
    cout << "Optimal DP (1D - Space Optimized): " << uniquePathsOptimized(m, n) << endl;
    
    return 0;
}