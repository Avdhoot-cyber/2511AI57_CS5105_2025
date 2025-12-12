#include <iostream>
#include <vector>
#include <string>
using namespace std;

// Brute force recursive helper
bool wildcardMatchBruteHelper(const string& s1, const string& s2, int i, int j) {
    int m = s1.size(), n = s2.size();
    if (i == m && j == n) return true;
    if (i == m) return false;
    if (j == n) {
        // If remaining characters in s1 are all '*'
        for (int k = i; k < m; ++k) {
            if (s1[k] != '*') return false;
        }
        return true;
    }

    if (s1[i] == s2[j] || s1[i] == '?') {
        return wildcardMatchBruteHelper(s1, s2, i + 1, j + 1);
    } else if (s1[i] == '*') {
        // '*' matches empty sequence or one or more chars
        return wildcardMatchBruteHelper(s1, s2, i + 1, j) || wildcardMatchBruteHelper(s1, s2, i, j + 1);
    }
    return false;
}

bool wildcardMatchBruteForce(const string& s1, const string& s2) {
    return wildcardMatchBruteHelper(s1, s2, 0, 0);
}

// Optimal DP approach
bool wildcardMatchOptimal(const string& s1, const string& s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<bool>> dp(m + 1, vector<bool>(n + 1, false));

    dp[0][0] = true;

    // Initialize dp for s2 empty and s1 prefix with stars
    for (int i = 1; i <= m; ++i) {
        if (s1[i - 1] == '*') dp[i][0] = dp[i - 1][0];
    }

    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (s1[i - 1] == s2[j - 1] || s1[i - 1] == '?') {
                dp[i][j] = dp[i - 1][j - 1];
            } else if (s1[i - 1] == '*') {
                dp[i][j] = dp[i - 1][j] || dp[i][j - 1];
            }
        }
    }
    return dp[m][n];
}

int main() {
    string s1, s2;
    
    cout << "Enter string S1 (pattern with ? and *): ";
    cin >> s1;
    
    cout << "Enter string S2 (text): ";
    cin >> s2;

    cout << "\n--- Results ---" << endl;
    if (s1.size() + s2.size() <= 20) {
        cout << "Brute Force: " << (wildcardMatchBruteForce(s1, s2) ? "True" : "False") << endl;
    } else {
        cout << "Brute Force: Skipped (input too large)" << endl;
    }
    cout << "Optimal DP: " << (wildcardMatchOptimal(s1, s2) ? "True" : "False") << endl;

    return 0;
}