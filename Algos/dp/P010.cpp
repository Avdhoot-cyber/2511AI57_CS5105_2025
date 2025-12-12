#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// Brute force recursive helper
int bruteHelper(const vector<vector<int>>& triangle, int row, int index) {
    int n = triangle.size();
    if (row == n - 1) return triangle[row][index];
    
    int down = bruteHelper(triangle, row + 1, index);
    int downRight = bruteHelper(triangle, row + 1, index + 1);
    
    return triangle[row][index] + min(down, downRight);
}

int minPathSumBruteForce(const vector<vector<int>>& triangle) {
    return bruteHelper(triangle, 0, 0);
}

// Optimal DP approach (bottom-up)
int minPathSumOptimal(const vector<vector<int>>& triangle) {
    int n = triangle.size();
    vector<int> dp(triangle.back()); // Initialize with bottom row
    
    for (int row = n - 2; row >= 0; --row) {
        for (int i = 0; i <= row; ++i) {
            dp[i] = triangle[row][i] + min(dp[i], dp[i + 1]);
        }
    }
    
    return dp[0];
}

// Main function with user input
int main() {
    int n;
    cout << "Enter number of rows in the triangle: ";
    cin >> n;
    
    vector<vector<int>> triangle(n);
    cout << "Enter the triangle values row-wise:" << endl;
    for (int i = 0; i < n; ++i) {
        triangle[i].resize(i + 1);
        for (int j = 0; j <= i; ++j) {
            cin >> triangle[i][j];
        }
    }
    
    cout << "\n--- Results ---" << endl;
    if (n <= 15) { // Limit to avoid exponential runtime in brute force
        cout << "Brute Force: " << minPathSumBruteForce(triangle) << endl;
    } else {
        cout << "Brute Force: Skipped (input too large)" << endl;
    }
    cout << "Optimal DP: " << minPathSumOptimal(triangle) << endl;
    
    return 0;
}