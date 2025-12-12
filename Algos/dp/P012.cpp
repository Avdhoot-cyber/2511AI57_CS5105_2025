#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int bruteHelper(const vector<vector<int>>& mat, int row, int colA, int colB) {
    int n = mat.size();
    int m = mat[0].size();

    if (colA < 0 || colA >= m || colB < 0 || colB >= m) return -1e9; // invalid

    if (row == n) return 0;

    int chocolates = (colA == colB) ? mat[row][colA] : mat[row][colA] + mat[row][colB];

    int maxChoc = -1e9;
    for (int dA = -1; dA <= 1; dA++) {
        for (int dB = -1; dB <= 1; dB++) {
            int nextChoc = bruteHelper(mat, row + 1, colA + dA, colB + dB);
            if (nextChoc != -1e9)
                maxChoc = max(maxChoc, chocolates + nextChoc);
        }
    }
    return maxChoc;
}

int maxChocolatesBruteForce(const vector<vector<int>>& mat) {
    int m = mat[0].size();
    return bruteHelper(mat, 0, 0, m - 1);
}

int dpHelper(const vector<vector<int>>& mat, int row, int colA, int colB, vector<vector<vector<int>>>& dp) {
    int n = mat.size();
    int m = mat[0].size();

    if (colA < 0 || colA >= m || colB < 0 || colB >= m) return -1e9;

    if (row == n) return 0;

    if (dp[row][colA][colB] != -1) return dp[row][colA][colB];

    int chocolates = (colA == colB) ? mat[row][colA] : mat[row][colA] + mat[row][colB];

    int maxChoc = -1e9;
    for (int dA = -1; dA <= 1; dA++) {
        for (int dB = -1; dB <= 1; dB++) {
            int nextChoc = dpHelper(mat, row + 1, colA + dA, colB + dB, dp);
            maxChoc = max(maxChoc, chocolates + nextChoc);
        }
    }
    return dp[row][colA][colB] = maxChoc;
}

int maxChocolatesOptimal(const vector<vector<int>>& mat) {
    int n = mat.size();
    int m = mat[0].size();
    vector<vector<vector<int>>> dp(n, vector<vector<int>>(m, vector<int>(m, -1)));
    return dpHelper(mat, 0, 0, m - 1, dp);
}

// Main function with user input
int main() {
    int n, m;
    cout << "Enter number of rows (N): ";
    cin >> n;
    cout << "Enter number of columns (M): ";
    cin >> m;

    vector<vector<int>> mat(n, vector<int>(m));
    cout << "Enter the chocolates matrix row-wise:" << endl;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < m; ++j)
            cin >> mat[i][j];

    cout << "\n--- Results ---" << endl;
    if (n <= 7 && m <= 7) { // Small constraints for brute force
        cout << "Brute Force: " << maxChocolatesBruteForce(mat) << endl;
    } else {
        cout << "Brute Force: Skipped for large input" << endl;
    }

    cout << "Optimal DP: " << maxChocolatesOptimal(mat) << endl;

    return 0;
}