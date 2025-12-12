#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// Brute-force recursive helper
int bruteHelper(const vector<int>& arr, int start, int end) {
    if (start > end) return 0;
    int robbed = arr[start] + bruteHelper(arr, start + 2, end);
    int skipped = bruteHelper(arr, start + 1, end);
    return max(robbed, skipped);
}

int robBruteForce(const vector<int>& arr) {
    int n = arr.size();
    if (n == 0) return 0;
    if (n == 1) return arr[0];
    int max1 = bruteHelper(arr, 0, n - 2);
    int max2 = bruteHelper(arr, 1, n - 1);
    return max(max1, max2);
}

// Optimal DP approach (O(n) time, O(1) space)
int robLinear(const vector<int>& arr, int start, int end) {
    int prev = 0, curr = 0;
    for (int i = start; i <= end; ++i) {
        int newRob = max(curr, prev + arr[i]);
        prev = curr;
        curr = newRob;
    }
    return curr;
}

int robOptimal(const vector<int>& arr) {
    int n = arr.size();
    if (n == 0) return 0;
    if (n == 1) return arr[0];
    int max1 = robLinear(arr, 0, n - 2);
    int max2 = robLinear(arr, 1, n - 1);
    return max(max1, max2);
}

// Main function with user input
int main() {
    int n;
    cout << "Enter the number of houses: ";
    cin >> n;
    
    vector<int> arr(n);
    cout << "Enter the money in each house: ";
    for (int i = 0; i < n; ++i) {
        cin >> arr[i];
    }
    
    cout << "\n--- Results ---" << endl;
    cout << "Brute Force: " << robBruteForce(arr) << endl;
    cout << "Optimal DP: " << robOptimal(arr) << endl;
    
    return 0;
}