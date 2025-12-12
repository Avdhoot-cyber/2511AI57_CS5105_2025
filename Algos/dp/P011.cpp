#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>
using namespace std;

// Brute force recursive helper
int bruteHelper(const vector<vector<int>>& matrix, int row, int col) {
    int n = matrix.size();
    int m = matrix[0].size();

    if (col < 0 || col >= m) return INT_MIN;
    if (row == n - 1) return matrix[row][col];

    int down = bruteHelper(matrix, row + 1, col);
    int downLeft = bruteHelper(matrix, row + 1, col - 1);
    int downRight = bruteHelper(matrix, row + 1, col + 1);

    return matrix[row][col] + max({down, downLeft, downRight});
}

int maxPathSumBruteForce(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();

    int maxSum = INT_MIN;
    for (int col = 0; col < m; ++col) {
        maxSum = max(maxSum, bruteHelper(matrix, 0, col));
    }
    return maxSum;
}

// Optimal DP approach
int maxPathSumOptimal(const vector<vector<int>>& matrix) {
    int n = matrix.size();
    int m = matrix[0].size();

    vector<vector<int>> dp(n, vector<int>(m, INT_MIN));

    // Initialize first row
    for (int j = 0; j < m; ++j) dp[0][j] = matrix[0][j];

    // Fill DP matrix
    for (int i = 1; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            int down = dp[i-1][j];
            int downLeft = (j - 1 >= 0) ? dp[i-1][j-1] : INT_MIN;
            int downRight = (j + 1 < m) ? dp[i-1][j+1] : INT_MIN;
            dp[i][j] = matrix[i][j] + max({down, downLeft, downRight});
        }
    }

    int maxSum = INT_MIN;
    for (int j = 0; j < m; ++j) {
        maxSum = max(maxSum, dp[n-1][j]);
    }
    return maxSum;
}

// Main with user input
int main() {
    int n, m;
    cout << "Enter number of rows (N): ";
    cin >> n;
    cout << "Enter number of columns (M): ";
    cin >> m;

    vector<vector<int>> matrix(n, vector<int>(m));
    cout << "Enter matrix values row-wise:" << endl;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cin >> matrix[i][j];
        }
    }

    cout << "\n--- Results ---" << endl;
    if (n <= 10) {
        cout << "Brute Force: " << maxPathSumBruteForce(matrix) << endl;
    } else {
        cout << "Brute Force: Skipped (too large input)" << endl;
    }
    cout << "Optimal DP: " << maxPathSumOptimal(matrix) << endl;

    return 0;
}