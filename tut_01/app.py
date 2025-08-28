"""
Student Group Management System
A comprehensive tool for creating balanced academic groups with multiple distribution strategies.
Author: [Your Name]
Date: [Current Date]
"""

import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque, defaultdict
import math
import requests
import base64
from pathlib import Path
import zipfile
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Configuration
CONFIG = {
    'app_title': 'Student Group Management System',
    'app_icon': '👥',
    'default_group_count': 15,
    'supported_file_types': ['xlsx'],
    'branch_priority': ["AI", "CB", "CE", "CH", "CS", "CT", "EC", "MC", "MM", "MT"]
}

@dataclass
class StudentRecord:
    """Data class representing a student record"""
    roll_number: str
    full_name: str
    email_address: str
    department: str

class BranchExtractor:
    """Utility class for extracting branch codes from roll numbers"""
    
    @staticmethod
    def get_department_code(roll_num: str) -> str:
        """Extract department code from student roll number"""
        if pd.isna(roll_num):
            return "UNKNOWN"
        
        pattern = re.search(r"[A-Z]{2}", str(roll_num))
        return pattern.group(0) if pattern else "UNKNOWN"

class GroupStatisticsGenerator:
    """Handles generation of group distribution statistics"""
    
    def __init__(self, groups: List[List], total_groups: int):
        self.groups = groups
        self.total_groups = total_groups
    
    def generate_statistics(self) -> pd.DataFrame:
        """Create comprehensive statistics table for group distribution"""
        # Extract all unique departments
        all_departments = set()
        for group in self.groups:
            if group:
                dept_list = [record.department for record in group if hasattr(record, 'department')]
                all_departments.update(dept_list)
        
        sorted_departments = sorted(list(all_departments))
        columns = sorted_departments + ["Total_Students"]
        
        # Initialize statistics matrix
        stats_matrix = pd.DataFrame(
            0, 
            index=[f"Group_{i+1}" for i in range(self.total_groups)], 
            columns=columns
        )
        
        # Populate statistics
        for idx, group in enumerate(self.groups, start=1):
            group_name = f"Group_{idx}"
            
            if group:
                # Count students by department
                dept_counts = defaultdict(int)
                for record in group:
                    if hasattr(record, 'department'):
                        dept_counts[record.department] += 1
                
                # Update statistics matrix
                for dept in sorted_departments:
                    stats_matrix.loc[group_name, dept] = dept_counts[dept]
                
                stats_matrix.loc[group_name, "Total_Students"] = len(group)
        
        return stats_matrix.reset_index().rename(columns={"index": "Group_ID"})

class BalancedDistributionStrategy:
    """Implements round-robin distribution strategy for balanced groups"""
    
    def __init__(self, student_data: pd.DataFrame, num_groups: int):
        self.student_data = student_data
        self.num_groups = num_groups
        self.department_queues = self._initialize_department_queues()
    
    def _initialize_department_queues(self) -> Dict[str, deque]:
        """Create department-wise queues maintaining original order"""
        available_departments = list(self.student_data["Department"].unique())
        
        # Prioritize departments based on configuration
        ordered_departments = [
            dept for dept in CONFIG['branch_priority'] 
            if dept in available_departments
        ] + [
            dept for dept in available_departments 
            if dept not in CONFIG['branch_priority']
        ]
        
        queues = {}
        for dept in ordered_departments:
            dept_students = self.student_data[self.student_data["Department"] == dept]
            queues[dept] = deque([
                StudentRecord(
                    roll_number=row["Roll_Number"],
                    full_name=row["Student_Name"], 
                    email_address=row["Email_Address"],
                    department=row["Department"]
                )
                for _, row in dept_students.iterrows()
            ])
        
        return queues
    
    def create_groups(self) -> List[List[StudentRecord]]:
        """Generate balanced groups using round-robin distribution"""
        total_students = len(self.student_data)
        base_size = total_students // self.num_groups
        extra_students = total_students % self.num_groups
        
        # Calculate target sizes for each group
        group_targets = [
            base_size + (1 if i < extra_students else 0) 
            for i in range(self.num_groups)
        ]
        
        groups = [[] for _ in range(self.num_groups)]
        
        # Distribute students using round-robin approach
        for group_idx in range(self.num_groups):
            target_size = group_targets[group_idx]
            
            while len(groups[group_idx]) < target_size:
                assigned_in_round = False
                
                # Try to assign one student from each department
                for dept, queue in self.department_queues.items():
                    if len(groups[group_idx]) >= target_size:
                        break
                    
                    if queue:  # If department has remaining students
                        student = queue.popleft()
                        groups[group_idx].append(student)
                        assigned_in_round = True
                
                # Break if no assignments were made (no students left)
                if not assigned_in_round:
                    break
        
        return groups

class DepartmentClusteringStrategy:
    """Implements department-based clustering strategy"""
    
    def __init__(self, student_data: pd.DataFrame, num_groups: int):
        self.student_data = student_data
        self.num_groups = num_groups
    
    def create_groups(self) -> List[List[StudentRecord]]:
        """Create groups by clustering departments together"""
        total_students = len(self.student_data)
        target_group_size = math.ceil(total_students / self.num_groups)
        
        # Sort departments by size (largest first)
        dept_counts = self.student_data["Department"].value_counts()
        sorted_departments = dept_counts.sort_values(ascending=False).index.tolist()
        
        # Create department-wise student collections
        dept_students = {}
        for dept in sorted_departments:
            dept_data = self.student_data[self.student_data["Department"] == dept]
            dept_students[dept] = [
                StudentRecord(
                    roll_number=row["Roll_Number"],
                    full_name=row["Student_Name"],
                    email_address=row["Email_Address"], 
                    department=row["Department"]
                )
                for _, row in dept_data.iterrows()
            ]
        
        groups = []
        remaining_blocks = []
        
        # Step 1: Create homogeneous department groups
        for dept, students in dept_students.items():
            dept_size = len(students)
            students_assigned = 0
            
            # Create full groups from this department
            while dept_size - students_assigned >= target_group_size:
                group = students[students_assigned:students_assigned + target_group_size]
                groups.append(group)
                students_assigned += target_group_size
            
            # Store remaining students as blocks
            if students_assigned < dept_size:
                remaining_block = students[students_assigned:]
                remaining_blocks.append(remaining_block)
        
        # Step 2: Combine remaining blocks to form mixed groups
        remaining_blocks.sort(key=len, reverse=True)  # Largest blocks first
        remaining_queue = deque(remaining_blocks)
        
        while remaining_queue:
            current_group = list(remaining_queue.popleft())
            available_space = target_group_size - len(current_group)
            
            # Fill remaining space with other blocks
            while available_space > 0 and remaining_queue:
                next_block = remaining_queue.popleft()
                
                if len(next_block) <= available_space:
                    # Add entire block
                    current_group.extend(next_block)
                    available_space -= len(next_block)
                else:
                    # Split block - take what fits, return remainder
                    fitting_portion = next_block[:available_space]
                    remaining_portion = next_block[available_space:]
                    
                    current_group.extend(fitting_portion)
                    remaining_queue.appendleft(remaining_portion)
                    available_space = 0
            
            groups.append(current_group)
        
        # Ensure we don't exceed requested group count
        if len(groups) > self.num_groups:
            raise ValueError(f"Algorithm created {len(groups)} groups, expected {self.num_groups}")
        
        # Add empty groups if needed
        while len(groups) < self.num_groups:
            groups.append([])
        
        return groups

class GitHubFileManager:
    """Manages file operations with GitHub repository"""
    
    def __init__(self, token: str, repo_owner: str, repo_name: str, base_path: str):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_path = base_path
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def upload_file(self, file_path: str, content: str) -> bool:
        """Upload a single file to GitHub repository"""
        api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        
        # Encode content for GitHub API
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": f"Add/Update {file_path}",
            "content": encoded_content,
            "branch": "main"
        }
        
        try:
            # Check if file already exists
            existing_file_response = requests.get(api_url, headers=self.headers)
            
            if existing_file_response.status_code == 200:
                # File exists - update it
                existing_data = existing_file_response.json()
                payload["sha"] = existing_data["sha"]
                payload["message"] = f"Update {file_path}"
            
            # Create or update file
            response = requests.put(api_url, headers=self.headers, json=payload)
            return response.status_code in [200, 201]
            
        except Exception as e:
            st.error(f"Failed to upload {file_path}: {e}")
            return False

class FileExportManager:
    """Handles various file export operations"""
    
    @staticmethod
    def create_department_csv_files(df: pd.DataFrame, github_manager: Optional[GitHubFileManager] = None) -> List[str]:
        """Generate CSV files organized by department"""
        created_files = []
        
        departments = df['Department'].unique()
        for dept in departments:
            if dept != "UNKNOWN":
                dept_data = df[df['Department'] == dept][['Roll_Number', 'Student_Name', 'Email_Address', 'Department']]
                
                if not dept_data.empty:
                    csv_content = dept_data.to_csv(index=False)
                    file_path = f"department_wise/{dept}.csv"
                    
                    if github_manager:
                        full_path = f"{github_manager.base_path}/{file_path}"
                        if github_manager.upload_file(full_path, csv_content):
                            created_files.append(full_path)
        
        return created_files
    
    @staticmethod
    def create_group_csv_files(groups: List[List[StudentRecord]], folder_name: str, 
                              github_manager: Optional[GitHubFileManager] = None) -> List[str]:
        """Generate CSV files for group collections"""
        created_files = []
        
        for idx, group in enumerate(groups, start=1):
            if group:  # Only create files for non-empty groups
                # Convert StudentRecord objects to DataFrame
                group_data = pd.DataFrame([
                    {
                        'Roll_Number': student.roll_number,
                        'Student_Name': student.full_name,
                        'Email_Address': student.email_address,
                        'Department': student.department
                    }
                    for student in group
                ])
                
                csv_content = group_data.to_csv(index=False)
                file_path = f"{folder_name}/Group_{idx}.csv"
                
                if github_manager:
                    full_path = f"{github_manager.base_path}/{file_path}"
                    if github_manager.upload_file(full_path, csv_content):
                        created_files.append(full_path)
        
        return created_files
    
    @staticmethod
    def create_download_package(df: pd.DataFrame, balanced_groups: List, 
                               clustered_groups: List, num_groups: int) -> BytesIO:
        """Create comprehensive download package as ZIP file"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
            
            # Add department-wise files
            departments = df['Department'].unique()
            for dept in departments:
                if dept != "UNKNOWN":
                    dept_data = df[df['Department'] == dept][['Roll_Number', 'Student_Name', 'Email_Address', 'Department']]
                    if not dept_data.empty:
                        csv_content = dept_data.to_csv(index=False)
                        zip_archive.writestr(f"department_wise/{dept}.csv", csv_content)
            
            # Add balanced distribution groups
            FileExportManager._add_groups_to_zip(zip_archive, balanced_groups, "balanced_distribution")
            
            # Add clustered groups
            FileExportManager._add_groups_to_zip(zip_archive, clustered_groups, "department_clustering")
            
            # Add statistics
            balanced_stats = GroupStatisticsGenerator(balanced_groups, num_groups).generate_statistics()
            clustered_stats = GroupStatisticsGenerator(clustered_groups, num_groups).generate_statistics()
            
            zip_archive.writestr("statistics_balanced.csv", balanced_stats.to_csv(index=False))
            zip_archive.writestr("statistics_clustered.csv", clustered_stats.to_csv(index=False))
        
        zip_buffer.seek(0)
        return zip_buffer
    
    @staticmethod
    def _add_groups_to_zip(zip_archive, groups: List, folder_name: str):
        """Helper method to add groups to ZIP archive"""
        for idx, group in enumerate(groups, start=1):
            if group:
                group_data = pd.DataFrame([
                    {
                        'Roll_Number': student.roll_number,
                        'Student_Name': student.full_name,
                        'Email_Address': student.email_address,
                        'Department': student.department
                    }
                    for student in group
                ])
                csv_content = group_data.to_csv(index=False)
                zip_archive.writestr(f"{folder_name}/Group_{idx}.csv", csv_content)

def initialize_application():
    """Configure Streamlit application settings"""
    st.set_page_config(
        page_title=CONFIG['app_title'],
        page_icon=CONFIG['app_icon'],
        layout="wide"
    )
    
    st.title(CONFIG['app_title'])
    st.caption("Advanced student grouping with multiple distribution strategies and GitHub integration.")

def process_student_data(uploaded_file) -> Optional[pd.DataFrame]:
    """Process and validate uploaded student data"""
    try:
        raw_data = pd.read_excel(uploaded_file)
        
        # Standardize column names
        required_columns = ["Roll", "Name", "Email"]
        column_mapping = {}
        
        for req_col in required_columns:
            if req_col not in raw_data.columns:
                raw_data[req_col] = ""
        
        # Create standardized DataFrame
        processed_data = pd.DataFrame({
            'Roll_Number': raw_data["Roll"],
            'Student_Name': raw_data["Name"],
            'Email_Address': raw_data["Email"]
        })
        
        # Extract department information
        processed_data['Department'] = processed_data['Roll_Number'].apply(
            BranchExtractor.get_department_code
        )
        
        return processed_data
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def display_group_preview(groups: List[List[StudentRecord]], title: str):
    """Display preview of generated groups"""
    with st.expander(f"Preview: {title}"):
        for idx, group in enumerate(groups, start=1):
            if group:
                st.markdown(f"**Group {idx}** ({len(group)} students)")
                
                group_df = pd.DataFrame([
                    {
                        'Roll Number': student.roll_number,
                        'Name': student.full_name,
                        'Email': student.email_address,
                        'Department': student.department
                    }
                    for student in group
                ])
                
                st.dataframe(group_df, use_container_width=True, hide_index=True)

def main_application():
    """Main application logic"""
    initialize_application()
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Student Data (Excel format)", 
        type=CONFIG['supported_file_types']
    )
    
    # Group configuration
    num_groups = st.number_input(
        "Number of Groups", 
        min_value=2, 
        max_value=50, 
        value=CONFIG['default_group_count'],
        step=1
    )
    
    # GitHub integration section
    with st.expander("GitHub Repository Integration"):
        st.markdown("""
        **Optional**: Connect to GitHub repository for automatic file uploads
        
        1. Create a Personal Access Token at: GitHub Settings > Developer Settings > Personal Access Tokens
        2. Grant 'repo' permissions to the token
        3. Enter the token below for automatic file uploads
        """)
        
        github_token = st.text_input(
            "GitHub Personal Access Token",
            type="password",
            help="Required for direct repository uploads"
        )
    
    if uploaded_file:
        # Process uploaded data
        student_data = process_student_data(uploaded_file)
        
        if student_data is not None:
            # Generate groups using different strategies
            balanced_strategy = BalancedDistributionStrategy(student_data, num_groups)
            balanced_groups = balanced_strategy.create_groups()
            
            clustering_strategy = DepartmentClusteringStrategy(student_data, num_groups)
            clustered_groups = clustering_strategy.create_groups()
            
            # Generate statistics
            balanced_stats = GroupStatisticsGenerator(balanced_groups, num_groups).generate_statistics()
            clustered_stats = GroupStatisticsGenerator(clustered_groups, num_groups).generate_statistics()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Students", len(student_data))
            col2.metric("Groups Created", num_groups)
            col3.metric("Average Group Size", f"{len(student_data)/num_groups:.1f}")
            col4.metric("Departments", student_data['Department'].nunique())
            
            # Display statistics
            st.subheader("Balanced Distribution Statistics")
            st.dataframe(balanced_stats, use_container_width=True, hide_index=True)
            
            st.subheader("Department Clustering Statistics")  
            st.dataframe(clustered_stats, use_container_width=True, hide_index=True)
            
            # Group previews
            display_group_preview(balanced_groups, "Balanced Distribution Groups")
            display_group_preview(clustered_groups, "Department Clustering Groups")
            
            # File operations
            github_manager = None
            if github_token:
                github_manager = GitHubFileManager(
                    token=github_token,
                    repo_owner="Avdhoot-cyber", 
                    repo_name="2511AI57_CS5105_2025",
                    base_path="tut_01"
                )
                
                # Upload files to GitHub
                created_files = []
                created_files.extend(FileExportManager.create_department_csv_files(student_data, github_manager))
                created_files.extend(FileExportManager.create_group_csv_files(balanced_groups, "balanced_distribution", github_manager))
                created_files.extend(FileExportManager.create_group_csv_files(clustered_groups, "department_clustering", github_manager))
                
                if created_files:
                    st.success(f"Successfully uploaded {len(created_files)} files to GitHub repository!")
                    st.info("View files at: https://github.com/Avdhoot-cyber/2511AI57_CS5105_2025/tree/main/tut_01")
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                # Excel export
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    balanced_stats.to_excel(writer, sheet_name="Balanced_Stats", index=False)
                    clustered_stats.to_excel(writer, sheet_name="Clustered_Stats", index=False)
                    
                    # Add group sheets
                    for idx, group in enumerate(balanced_groups, start=1):
                        if group:
                            group_df = pd.DataFrame([
                                {
                                    'Roll_Number': s.roll_number,
                                    'Student_Name': s.full_name,
                                    'Email_Address': s.email_address,
                                    'Department': s.department
                                } for s in group
                            ])
                            group_df.to_excel(writer, sheet_name=f"Balanced_Group_{idx}", index=False)
                
                excel_buffer.seek(0)
                
                st.download_button(
                    label="Download Excel Report",
                    data=excel_buffer,
                    file_name="student_groups_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # ZIP package export
                zip_package = FileExportManager.create_download_package(
                    student_data, balanced_groups, clustered_groups, num_groups
                )
                
                st.download_button(
                    label="Download CSV Package",
                    data=zip_package,
                    file_name="student_groups_package.zip",
                    mime="application/zip"
                )

if __name__ == "__main__":
    main_application()
