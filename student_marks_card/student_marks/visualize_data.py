import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .models import Marks, Student, Subject
import io
import base64
from django.db.models import Avg, Max, Min, Count
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Configure matplotlib settings
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.autolayout'] = True

def get_base64_graph(fig):
    """Convert matplotlib figure to base64 string"""
    try:
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=300)
        buffer.seek(0)
        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png).decode('utf-8')
        plt.close(fig)  # Close the figure before closing the buffer
        return graph
    except Exception as e:
        logger.error(f"Error converting figure to base64: {e}")
        return None
    finally:
        buffer.close()

def subject_wise_analysis(marks_data):
    """Subject-wise Analysis"""
    try:
        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(marks_data.values('subject__name', 'score')))
        if df.empty:
            logger.warning("No data available for subject-wise analysis")
            return None, None
            
        plt.clf()
        plt.style.use('default')
        sns.set_theme(style="whitegrid")
        
        # Create figure with larger size
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use boxplot and stripplot instead of swarmplot
        sns.boxplot(data=df, x='subject__name', y='score', ax=ax)
        sns.stripplot(data=df, x='subject__name', y='score', color='.3', 
                     size=3, alpha=0.4, jitter=0.2)
        
        plt.xticks(rotation=45)
        plt.title('Subject-wise Score Distribution')
        plt.xlabel('Subjects')
        plt.ylabel('Scores')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Calculate statistics
        stats = df.groupby('subject__name')['score'].agg(['mean', 'std', 'min', 'max']).round(2)
        
        return get_base64_graph(fig), stats.to_dict('index')
        
    except Exception as e:
        logger.error(f"Error in subject_wise_analysis: {e}")
        return None, None

def student_performance_analysis(marks_data):
    """छात्र प्रदर्शन विश्लेषण करें"""
    try:
        # Convert QuerySet to DataFrame
        df = pd.DataFrame(list(marks_data.values('student__full_name', 'score')))
        if df.empty:
            logger.warning("No data available for student performance analysis")
            return None
            
        plt.clf()
        plt.style.use('default')
        sns.set_theme(style="whitegrid")
        
        # Create figure with larger size
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use boxplot and stripplot combination
        sns.boxplot(data=df, x='student__full_name', y='score', ax=ax)
        sns.stripplot(data=df, x='student__full_name', y='score', 
                     color='.3', size=3, alpha=0.4, jitter=0.2)
        
        plt.xticks(rotation=45, ha='right')
        plt.title('Student Performance Distribution')
        plt.xlabel('Students')
        plt.ylabel('Scores')
        
        # Adjust layout
        plt.tight_layout()
        
        return get_base64_graph(fig)
        
    except Exception as e:
        logger.error(f"Error in student_performance_analysis: {e}")
        return None

def class_wise_analysis(marks_queryset):
    """Class-wise Analysis"""
    try:
        df = pd.DataFrame(list(marks_queryset.values(
            'student__student_class__name', 'subject__name', 'score'
        )))
        
        if df.empty:
            return None
        
        plt.clf()  # Clear any existing plots
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Bar Chart - Class Average
        plt.subplot(2, 2, 1)
        class_avg = df.groupby('student__student_class__name')['score'].mean()
        sns.barplot(x=class_avg.index, y=class_avg.values)
        plt.title('Class-wise Average Score')
        plt.xticks(rotation=45)
        plt.ylabel('Average Score')
        
        # 2. Box Plot - Score Distribution
        plt.subplot(2, 2, 2)
        sns.boxplot(x='student__student_class__name', y='score', data=df)
        plt.title('Class-wise Score Distribution')
        plt.xticks(rotation=45)
        plt.ylabel('Score')
        
        # 3. Heatmap - Class vs Subject
        plt.subplot(2, 2, 3)
        class_subject_scores = df.pivot_table(
            values='score',
            index='student__student_class__name',
            columns='subject__name',
            aggfunc='mean'
        )
        sns.heatmap(class_subject_scores, annot=True, cmap='YlOrRd', fmt='.0f')
        plt.title('Class-Subject Score Heatmap')
        plt.xticks(rotation=45)
        
        # 4. Violin Plot - Detailed Distribution
        plt.subplot(2, 2, 4)
        sns.violinplot(x='student__student_class__name', y='score', data=df)
        plt.title('Detailed Score Distribution by Class')
        plt.xticks(rotation=45)
        plt.ylabel('Score')
        
        plt.tight_layout()
        return get_base64_graph(fig)
        
    except Exception as e:
        logger.error(f"Error in class_wise_analysis: {e}")
        return None

def get_top_performers(marks_queryset, n=10):
    """Top Performers List"""
    try:
        df = pd.DataFrame(list(marks_queryset.values(
            'student__full_name', 'subject__name', 'score'
        )))
        
        if df.empty:
            return "No data available", "No data available"
        
        # Subject-wise top performers
        subject_toppers = df.groupby(['subject__name', 'student__full_name'])['score'].mean().reset_index()
        subject_toppers = subject_toppers.sort_values(['subject__name', 'score'], ascending=[True, False])
        subject_toppers = subject_toppers.groupby('subject__name').head(n)
        
        # Format subject-wise toppers table
        subject_toppers = subject_toppers.rename(columns={
            'student__full_name': 'Student Name',
            'subject__name': 'Subject',
            'score': 'Score'
        })
        subject_html = subject_toppers.to_html(
            classes='table table-striped table-sm table-hover',
            float_format=lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x,
            index=False
        )
        
        # Overall top performers
        total_toppers = df.groupby('student__full_name').agg({
            'score': ['sum', 'mean', 'count']
        }).round(2)
        total_toppers.columns = ['Total Score', 'Average Score', 'Number of Subjects']
        total_toppers = total_toppers.sort_values('Total Score', ascending=False).head(n)
        
        # Format overall toppers table
        total_toppers = total_toppers.reset_index()
        total_toppers = total_toppers.rename(columns={'student__full_name': 'Student Name'})
        total_html = total_toppers.to_html(
            classes='table table-striped table-sm table-hover',
            float_format=lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x,
            index=False
        )
        
        return subject_html, total_html
        
    except Exception as e:
        logger.error(f"Error in get_top_performers: {e}")
        return "Error getting top performers", "Error getting top performers"

def generate_student_report(student_marks):
    """Individual Student Report"""
    try:
        df = pd.DataFrame(list(student_marks.values(
            'subject__name', 'score', 'exam_date'
        )))
        
        if df.empty:
            return None
            
        plt.clf()  # Clear any existing plots
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Radar Chart - Subject Performance
        plt.subplot(2, 2, 1, projection='polar')
        subjects = df['subject__name'].unique()
        scores = df.groupby('subject__name')['score'].mean()
        angles = np.linspace(0, 2*np.pi, len(subjects), endpoint=False)
        
        plt.plot(angles, scores)
        plt.fill(angles, scores, alpha=0.25)
        plt.xticks(angles, subjects)
        plt.title('Subject-wise Performance')
        
        # 2. Line Chart - Performance Over Time
        plt.subplot(2, 2, 2)
        time_series = df.pivot_table(
            values='score',
            index='exam_date',
            columns='subject__name',
            aggfunc='mean'
        )
        time_series.plot(marker='o')
        plt.title('Performance Over Time')
        plt.xticks(rotation=45)
        plt.ylabel('Score')
        
        # 3. Bar Chart - Average Scores
        plt.subplot(2, 2, 3)
        avg_scores = df.groupby('subject__name')['score'].mean()
        avg_scores.plot(kind='bar')
        plt.title('Subject-wise Average Score')
        plt.xticks(rotation=45)
        plt.ylabel('Score')
        
        plt.tight_layout()
        return get_base64_graph(fig)
        
    except Exception as e:
        logger.error(f"Error in generate_student_report: {e}")
        return None
