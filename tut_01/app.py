import streamlit as st
import pandas as pd
from io import BytesIO
import re
from collections import deque
import math

# Configuration and constants
APP_CONFIG = {
    'title': 'Group Stats Generator',
    'icon': ' ',
    'layout': 'wide',
    'default_team_count': 15,
    'file_types': ['xlsx'],
    'required_columns': ['Roll', 'Name', 'Email']
}

DEPARTMENT_HIERARCHY = ["AI", "CB", "CE", "CH", "CS", "CT", "EC", "MC", "MM", "MT"]

class StudentDataProcessor:
    """Handles student data processing and branch extraction"""
    
    def __init__(self):
        self.branch_pattern = r"[A-Z]{2}"
    
    def get_department_code(self, student_roll):
        """Extracts department code from student roll number"""
        if pd.isna(student_roll):
            return "??"
        pattern_match = re.search(self.branch_pattern, str(student_roll))
        return pattern_match.group(0) if pattern_match else "??"
    
    def validate_dataframe(self, dataframe):
        """Ensures all required columns exist in the dataframe"""
        for required_col in APP_CONFIG['required_columns']:
            if required_col not in dataframe.columns:
                dataframe[required_col] = ""
        return dataframe

class StatisticsCalculator:
    """Generates statistical summaries for team distributions"""
    
    def compute_team_statistics(self, team_collections, total_teams):
        """Creates comprehensive statistics table for all teams"""
        department_set = set()
        
        # Gather all departments from non-empty teams
        for team_data in team_collections:
            if team_data:
                team_df = pd.DataFrame(team_data)
                department_set.update(team_df["Branch"].tolist())
        
        sorted_departments = sorted(list(department_set))
        team_labels = [f"G{idx+1}" for idx in range(total_teams)]
        
        # Initialize statistics matrix
        statistics_matrix = pd.DataFrame(
            0, 
            index=team_labels, 
            columns=sorted_departments + ["Total"]
        )
        
        # Populate statistics for each team
        for team_idx, team_members in enumerate(team_collections):
            team_label = f"G{team_idx+1}"
            if team_members:
                member_df = pd.DataFrame(team_members)
                
                # Count members per department
                for dept in sorted_departments:
                    dept_count = (member_df["Branch"] == dept).sum()
                    statistics_matrix.loc[team_label, dept] = int(dept_count)
                
                # Total members in team
                statistics_matrix.loc[team_label, "Total"] = int(len(member_df))
        
        return statistics_matrix.reset_index().rename(columns={"index": "Group"})

class TeamFormationStrategy:
    """Implements different strategies for forming teams"""
    
    def __init__(self):
        self.processor = StudentDataProcessor()
    
    def balanced_round_robin_allocation(self, student_df, num_teams):
        """
        Distributes students using round-robin within departments per team
        """
        # Get departments in preferred order
        available_depts = list(pd.unique(student_df["Branch"]))
        ordered_depts = []
        
        # Add departments in hierarchy order first
        for dept in DEPARTMENT_HIERARCHY:
            if dept in available_depts:
                ordered_depts.append(dept)
        
        # Add remaining departments not in hierarchy
        for dept in available_depts:
            if dept not in DEPARTMENT_HIERARCHY:
                ordered_depts.append(dept)
        
        # Create department-wise student queues
        dept_student_queues = {}
        for department in ordered_depts:
            dept_students = student_df[student_df["Branch"] == department]
            student_list = [student_record for _, student_record in dept_students.iterrows()]
            dept_student_queues[department] = deque(student_list)
        
        # Calculate balanced team sizes
        total_students = len(student_df)
        base_team_size = total_students // num_teams
        extra_slots = total_students % num_teams
        
        team_targets = []
        for team_idx in range(num_teams):
            target_size = base_team_size + (1 if team_idx < extra_slots else 0)
            team_targets.append(target_size)
        
        # Initialize empty teams
        formed_teams = [[] for _ in range(num_teams)]
        
        # Fill teams using round-robin allocation
        for team_idx in range(num_teams):
            current_target = team_targets[team_idx]
            
            while len(formed_teams[team_idx]) < current_target:
                allocation_made = False
                
                for dept in ordered_depts:
                    if len(formed_teams[team_idx]) >= current_target:
                        break
                    
                    if dept_student_queues[dept]:
                        student = dept_student_queues[dept].popleft()
                        formed_teams[team_idx].append(student)
                        allocation_made = True
                
                if not allocation_made:
                    break
        
        return formed_teams
    
    def homogeneous_block_allocation(self, student_df, num_teams):
        """
        Creates teams by grouping students from same departments together
        """
        total_students = len(student_df)
        optimal_team_size = math.ceil(total_students / num_teams)
        final_teams = []
        
        # Get department counts in descending order
        dept_distribution = student_df["Branch"].value_counts()
        sorted_departments = list(dept_distribution.sort_values(ascending=False).index)
        
        # Organize students by department maintaining original order
        dept_student_groups = {}
        for dept in sorted_departments:
            dept_students = student_df[student_df["Branch"] == dept]
            student_records = [record for _, record in dept_students.iterrows()]
            dept_student_groups[dept] = student_records
        
        remaining_blocks = []
        
        # Phase 1: Create homogeneous teams and collect remainder blocks
        for dept in sorted_departments:
            students_in_dept = dept_student_groups[dept]
            dept_size = len(students_in_dept)
            processed_count = 0
            
            # Form complete teams from this department
            while dept_size - processed_count >= optimal_team_size:
                team_block = students_in_dept[processed_count:processed_count + optimal_team_size]
                final_teams.append(team_block)
                processed_count += optimal_team_size
            
            # Save remaining students as a block
            if processed_count < dept_size:
                remainder_block = students_in_dept[processed_count:]
                remaining_blocks.append(remainder_block)
        
        # Sort remaining blocks by size (largest first)
        remaining_blocks.sort(key=lambda block: len(block), reverse=True)
        remaining_blocks = deque(remaining_blocks)
        
        # Phase 2: Form mixed teams from remaining blocks
        while remaining_blocks:
            # Start new team with largest remaining block
            primary_block = remaining_blocks.popleft()
            mixed_team = list(primary_block)
            available_space = optimal_team_size - len(mixed_team)
            
            # Fill remaining space with other blocks
            while available_space > 0 and remaining_blocks:
                next_block = remaining_blocks.popleft()
                
                if len(next_block) <= available_space:
                    # Entire block fits
                    mixed_team.extend(next_block)
                    available_space -= len(next_block)
                else:
                    # Partial block fits, split it
                    fitting_portion = next_block[:available_space]
                    remaining_portion = next_block[available_space:]
                    
                    mixed_team.extend(fitting_portion)
                    remaining_blocks.appendleft(remaining_portion)
                    available_space = 0
            
            final_teams.append(mixed_team)
        
        # Validate team count
        if len(final_teams) > num_teams:
            raise ValueError(f"Generated {len(final_teams)} teams, expected {num_teams}")
        
        # Ensure we have exactly the requested number of teams
        while len(final_teams) < num_teams:
            final_teams.append([])
        
        return final_teams

def initialize_streamlit_app():
    """Sets up the Streamlit application configuration"""
    st.set_page_config(
        page_title=APP_CONFIG['title'],
        page_icon=APP_CONFIG['icon'],
        layout=APP_CONFIG['layout']
    )
    
    st.title(APP_CONFIG['title'])
    st.caption("Upload one Excel file with all students (Roll, Name, Email) and get group-wise stats + download.")

def create_download_package(balanced_teams, homogeneous_teams, balanced_stats, homogeneous_stats):
    """Generates Excel file with all team data and statistics"""
    excel_buffer = BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as excel_writer:
        # Write statistics sheets
        balanced_stats.to_excel(excel_writer, sheet_name="Stats_Mixed", index=False)
        homogeneous_stats.to_excel(excel_writer, sheet_name="Stats_Uniform", index=False)
        
        # Write individual team sheets for balanced strategy
        for team_idx, team_members in enumerate(balanced_teams, start=1):
            if team_members:
                team_dataframe = pd.DataFrame(team_members)
                sheet_name = f"Mixed_G{team_idx}"
                team_dataframe.to_excel(excel_writer, sheet_name=sheet_name, index=False)
        
        # Write individual team sheets for homogeneous strategy
        for team_idx, team_members in enumerate(homogeneous_teams, start=1):
            if team_members:
                team_dataframe = pd.DataFrame(team_members)
                sheet_name = f"Uniform_G{team_idx}"
                team_dataframe.to_excel(excel_writer, sheet_name=sheet_name, index=False)
    
    excel_buffer.seek(0)
    return excel_buffer

def display_team_preview(teams_data, strategy_name):
    """Shows expandable preview of team compositions"""
    with st.expander(f" Preview {strategy_name} Groups"):
        for team_number, team_members in enumerate(teams_data, start=1):
            st.markdown(f"*G{team_number}*")
            if team_members:
                team_display_df = pd.DataFrame(team_members)
                display_columns = ["Roll", "Name", "Email", "Branch"]
                st.dataframe(
                    team_display_df[display_columns], 
                    use_container_width=True, 
                    hide_index=True
                )

def execute_main_application():
    """Main application execution logic"""
    # Initialize components
    data_processor = StudentDataProcessor()
    stats_calculator = StatisticsCalculator()
    team_formation = TeamFormationStrategy()
    
    # UI Components
    uploaded_excel = st.file_uploader(
        "Upload input_Make Groups.xlsx", 
        type=APP_CONFIG['file_types']
    )
    
    team_count = st.number_input(
        "Number of groups",
        min_value=2,
        max_value=100,
        value=APP_CONFIG['default_team_count'],
        step=1
    )
    
    if uploaded_excel is not None:
        try:
            # Load and process data
            raw_dataframe = pd.read_excel(uploaded_excel)
            processed_df = data_processor.validate_dataframe(raw_dataframe)
            processed_df["Branch"] = processed_df["Roll"].apply(data_processor.get_department_code)
            
            # Generate teams using both strategies
            balanced_teams = team_formation.balanced_round_robin_allocation(processed_df, team_count)
            homogeneous_teams = team_formation.homogeneous_block_allocation(processed_df, team_count)
            
            # Calculate statistics
            balanced_statistics = stats_calculator.compute_team_statistics(balanced_teams, team_count)
            homogeneous_statistics = stats_calculator.compute_team_statistics(homogeneous_teams, team_count)
            
            # Display metrics
            metrics_cols = st.columns(4)
            metrics_cols[0].metric("Students", f"{len(processed_df)}")
            metrics_cols[1].metric("Groups", f"{team_count}")
            metrics_cols[2].metric("Avg / Group", f"{(len(processed_df)/team_count):.2f}")
            metrics_cols[3].metric("Branches", f"{processed_df['Branch'].nunique()}")
            
            # Display statistics tables
            st.subheader(" Stats - Mixed Strategy (Branch-wise RR per group)")
            st.dataframe(balanced_statistics, use_container_width=True, hide_index=True)
            
            st.subheader(" Stats - Uniform Strategy")
            st.dataframe(homogeneous_statistics, use_container_width=True, hide_index=True)
            
            # Show team previews
            display_team_preview(balanced_teams, "Mixed")
            display_team_preview(homogeneous_teams, "Uniform")
            
            # Generate download package
            download_data = create_download_package(
                balanced_teams, 
                homogeneous_teams,
                balanced_statistics,
                homogeneous_statistics
            )
            
            # Download button
            st.download_button(
                label="⬇ Download output.xlsx",
                data=download_data,
                file_name="output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            
        except Exception as error:
            st.error(f"Could not read file: {error}")

# Application entry point
if __name__ == "__main__":
    initialize_streamlit_app()
    execute_main_application()
