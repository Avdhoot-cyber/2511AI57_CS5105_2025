#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

// Brute force recursive helper
int bruteHelper(const vector<vector<int>>& matrix, int i, int j, int n, int m) {
    // Base case: reached destination
    if (i == n - 1 && j == m - 1) return matrix[i][j];
    
    // Out of bounds
    if (i >= n || j >= m) return INT_MAX;
    
    // Move down
    int down = bruteHelper(matrix, i + 1, j, n, m);
    // Move right
    int right = bruteHelper(matrix, i, j + 1, n, m);
    
    // Return current cell value + minimum of both paths
    if (down == INT_MAX && right == INT_MAX) return INT_MAX;
    return matrix[i][j] + min(down, right);
}

int minPathSumBruteForce(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();
    return bruteHelper(matrix, 0, 0, n, m);
}

// Optimal DP approach (2D array)
int minPathSumOptimal(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();
    
    vector<vector<int>> dp(n, vector<int>(m, 0));
    
    // Initialize starting cell
    dp[0][0] = matrix[0][0];
    
    // Initialize first row
    for (int j = 1; j < m; ++j) {
        dp[0][j] = dp[0][j - 1] + matrix[0][j];
    }
    
    // Initialize first column
    for (int i = 1; i < n; ++i) {
        dp[i][0] = dp[i - 1][0] + matrix[i][0];
    }
    
    // Fill the DP table
    for (int i = 1; i < n; ++i) {
        for (int j = 1; j < m; ++j) {
            dp[i][j] = matrix[i][j] + min(dp[i - 1][j], dp[i][j - 1]);
        }
    }
    
    return dp[n - 1][m - 1];
}

// Optimal DP approach (Space Optimized - 1D array)
int minPathSumOptimized(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();
    
    vector<int> dp(m, 0);
    
    // Initialize first row
    dp[0] = matrix[0][0];
    for (int j = 1; j < m; ++j) {
        dp[j] = dp[j - 1] + matrix[0][j];
    }
    
    // Process remaining rows
    for (int i = 1; i < n; ++i) {
        dp[0] = dp[0] + matrix[i][0]; // First column
        for (int j = 1; j < m; ++j) {
            dp[j] = matrix[i][j] + min(dp[j], dp[j - 1]);
        }
    }
    
    return dp[m - 1];
}

// Main function with user input
int main() {
    int n, m;
    cout << "Enter number of rows (N): ";
    cin >> n;
    cout << "Enter number of columns (M): ";
    cin >> m;
    
    vector<vector<int>> matrix(n, vector<int>(m));
    cout << "Enter the matrix values:" << endl;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cin >> matrix[i][j];
        }
    }
    
    cout << "\n--- Results ---" << endl;
    
    // Note: Brute force can be very slow for larger inputs
    if (n <= 10 && m <= 10) {
        cout << "Brute Force: " << minPathSumBruteForce(matrix) << endl;
    } else {
        cout << "Brute Force: Skipped (too large, would take too long)" << endl;
    }
    
    cout << "Optimal DP (2D): " << minPathSumOptimal(matrix) << endl;
    cout << "Optimal DP (1D - Space Optimized): " << minPathSumOptimized(matrix) << endl;
    
    return 0;
}