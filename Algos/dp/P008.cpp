#include <iostream>
#include <vector>
using namespace std;

// Brute force recursive helper
int bruteHelper(const vector<vector<int>>& maze, int i, int j, int n, int m) {
    // If out of bounds or blocked cell
    if (i >= n || j >= m || maze[i][j] == -1) return 0;
    // If reached destination
    if (i == n - 1 && j == m - 1) return 1;
    // Move down + move right
    return bruteHelper(maze, i + 1, j, n, m) + bruteHelper(maze, i, j + 1, n, m);
}

int uniquePathsBruteForce(const vector<vector<int>>& maze) {
    int n = maze.size();
    int m = maze[0].size();
    return bruteHelper(maze, 0, 0, n, m);
}

// Optimal DP approach
int uniquePathsOptimal(const vector<vector<int>>& maze) {
    int n = maze.size();
    int m = maze[0].size();

    vector<vector<int>> dp(n, vector<int>(m, 0));

    // Initialize first cell if not blocked
    dp[0][0] = (maze[0][0] == 0) ? 1 : 0;

    // First column
    for (int i = 1; i < n; ++i) {
        dp[i][0] = (maze[i][0] == 0 && dp[i-1][0] == 1) ? 1 : 0;
    }

    // First row
    for (int j = 1; j < m; ++j) {
        dp[0][j] = (maze[0][j] == 0 && dp[0][j-1] == 1) ? 1 : 0;
    }

    // Fill dp table
    for (int i = 1; i < n; ++i) {
        for (int j = 1; j < m; ++j) {
            if (maze[i][j] == 0) {
                dp[i][j] = dp[i-1][j] + dp[i][j-1];
            } else {
                dp[i][j] = 0;
            }
        }
    }

    return dp[n-1][m-1];
}

// Main function with user input
int main() {
    int n, m;
    cout << "Enter number of rows (N): ";
    cin >> n;
    cout << "Enter number of columns (M): ";
    cin >> m;

    vector<vector<int>> maze(n, vector<int>(m));
    cout << "Enter the maze matrix (-1 for blocked cell, 0 for free cell):" << endl;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cin >> maze[i][j];
        }
    }

    cout << "\n--- Results ---" << endl;
    if (n <= 10 && m <= 10) {
        cout << "Brute Force: " << uniquePathsBruteForce(maze) << endl;
    } else {
        cout << "Brute Force: Skipped due to large input size" << endl;
    }
    cout << "Optimal DP: " << uniquePathsOptimal(maze) << endl;

    return 0;
}