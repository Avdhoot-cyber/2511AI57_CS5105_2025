//4 5 4 A = {{1,1},{0,1},{3,3},{3,4}}

#include<bits/stdc++.h>
using namespace std;



class DisjointSet{
public:
    vector<int> parent,rank;
    DisjointSet(int n){
        parent.resize(n);
        rank.resize(n,0);
        
        for(int i=0;i<n;i++){
            parent[i] = i;
        }
        
    }
    
    int findUPar(int a){
        if(parent[a]==a){
            return a;
        }
        
        return parent[a] = findUPar(parent[a]);
    }
    
    void UnionbyRank(int a,int b){
        int p_a = findUPar(a),p_b = findUPar(b);
        
        if(p_a==p_b) return;
        
        if(rank[p_a]==rank[p_b]){
            rank[p_a]++;
            parent[p_b] = p_a;
        }else if(rank[p_a]>rank[p_b]){
            parent[p_b] = p_a;
        }else{
            parent[p_a] = p_b;
        }
    }
       
};

//4 5 {{1,1},{0,1},{3,3},{3,4}}

class Solution {
  public:
    vector<int> numOfIslands(int n, int m, vector<vector<int>> &operators) {
        vector<int> order;
        DisjointSet dsu(n*m);
        vector<vector<int>> mat(n,vector<int>(m));
        int dx[] = {1,0,-1,0},dy[] = {0,-1,0,1},count = 0;
        for(auto &op:operators){
            int row = op[0],col = op[1];
            if(mat[row][col]==1){
                order.push_back(count);
                continue;
            };
            mat[row][col] = 1;
            count++;
            int srcVal = row*m+col;
            for(int k=0;k<4;k++){
                int nr = row+dx[k],nc = col+dy[k];
                if(nr>=0 && nr<n && nc>=0 && nc<m && mat[nr][nc]==1){
                    int val = nr*m+nc;
                    int p_src = findUPar(srcVal), p_val = findUPar(val);
                    if(p_src!=p_val){
                        dsu.UnionbyRank(srcVal,val);
                        count--;
                    }
                    
                }
            }
            
            order.push_back(count);
        }
        return order;
    }
};

vector<vector<int>> makeEdges(string s){
    int j=0;
    vector<int> temp;
    string num = "";
    vector<vector<int>> mat;
    for(int i=0;i<s.length();i++){
        if(i==0){
            continue;
        }
        if(isdigit(s[i]) || s[i]=='-'){
            num+=s[i];
        }else if(!num.empty()){
            temp.push_back(stoi(num));
            num = "";
            j++;
            }
        
        
        if(j==2){
            mat.push_back(temp);
            temp.clear();
            j = 0;
        }
    }
    return mat;
}

void printVec(vector<int> &v){
    cout<<"[";
    for(int i=0;i<v.size();i++){
        cout<<v[i]<<" ";
    }
    cout<<"]";
}

int main(){
    int n,m;
    cin>>n>>m;
    string s;
    cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    getline(cin,s);
    vector<vector<int>> edges = makeEdges(s);
    Solution S;
    vector<int> order = S.numOfIslands(n,m,edges);
    printVec(order);
    return 0;
}

