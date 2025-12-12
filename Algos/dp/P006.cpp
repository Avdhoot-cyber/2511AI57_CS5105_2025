#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// Brute-force recursive helper
int bruteHelper(const vector<vector<int>>& points, int day, int last) {
    if (day < 0) return 0;
    int maxi = 0;
    for (int task = 0; task < 3; ++task) {
        if (task != last) {
            int point = points[day][task] + bruteHelper(points, day - 1, task);
            maxi = max(maxi, point);
        }
    }
    return maxi;
}

int ninjaBruteForce(const vector<vector<int>>& points) {
    int n = points.size();
    return bruteHelper(points, n - 1, 3); // 3 denotes 'no task done last day'
}

// Optimal DP
int ninjaOptimal(const vector<vector<int>>& points) {
    int n = points.size();
    vector<vector<int>> dp(n, vector<int>(4, 0));
    // Base case
    dp[0][0] = max(points[0][1], points[0][2]);
    dp[0][1] = max(points[0][0], points[0][2]);
    dp[0][2] = max(points[0][0], points[0][1]);
    dp[0][3] = max({points[0][0], points[0][1], points[0][2]});

    for (int day = 1; day < n; ++day) {
        for (int last = 0; last < 4; ++last) {
            dp[day][last] = 0;
            for (int task = 0; task < 3; ++task) {
                if (task != last) {
                    int curr = points[day][task] + dp[day - 1][task];
                    dp[day][last] = max(dp[day][last], curr);
                }
            }
        }
    }
    return dp[n - 1][3];
}

// Main function for user input
int main() {
    int n;
    cout << "Enter number of days: ";
    cin >> n;
    vector<vector<int>> points(n, vector<int>(3));
    cout << "Enter merit points for each day (3 per day):" << endl;
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < 3; ++j) {
            cin >> points[i][j];
        }
    }

    cout << "\n--- Results ---" << endl;
    cout << "Brute Force: " << ninjaBruteForce(points) << endl;
    cout << "Optimal DP: " << ninjaOptimal(points) << endl;

    return 0;
}