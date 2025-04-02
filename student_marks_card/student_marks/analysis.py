import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Avg, Max, Min, Count
import logging

logger = logging.getLogger(__name__)

def subject_wise_analysis(marks):
    """Generate subject-wise analysis of marks"""
    try:
        # Convert queryset to DataFrame
        df = pd.DataFrame(list(marks.values(
            'subject__name', 'score', 'student__full_name'
        )))
        
        if df.empty:
            return None, None
        
        # Calculate statistics
        stats = df.groupby('subject__name').agg({
            'score': ['mean', 'min', 'max', 'count']
        }).round(2)
        stats.columns = ['Average', 'Minimum', 'Maximum', 'Count']
        stats = stats.reset_index()
        
        # Create bar plot
        fig = px.bar(
            stats,
            x='subject__name',
            y='Average',
            title='Subject-wise Average Scores',
            labels={'subject__name': 'Subject', 'Average': 'Average Score'},
            color='Average',
            color_continuous_scale='viridis'
        )
        
        plot_html = fig.to_html(full_html=False)
        return plot_html, stats.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error in subject_wise_analysis: {e}", exc_info=True)
        return None, None

def student_performance_analysis(marks):
    """Generate student performance analysis"""
    try:
        # Convert queryset to DataFrame
        df = pd.DataFrame(list(marks.values(
            'student__full_name', 'score', 'subject__name', 'exam_date__date_of_exam'
        )))
        
        if df.empty:
            return None
        
        # Calculate average score per student
        student_avg = df.groupby('student__full_name')['score'].mean().round(2)
        
        # Create bar plot
        fig = px.bar(
            x=student_avg.index,
            y=student_avg.values,
            title='Student Performance Comparison',
            labels={'x': 'Student', 'y': 'Average Score'},
            color=student_avg.values,
            color_continuous_scale='viridis'
        )
        
        return fig.to_html(full_html=False)
        
    except Exception as e:
        logger.error(f"Error in student_performance_analysis: {e}", exc_info=True)
        return None

def class_wise_analysis(marks):
    """Generate class-wise analysis"""
    try:
        # Convert queryset to DataFrame
        df = pd.DataFrame(list(marks.values(
            'student__student_class__name', 'score'
        )))
        
        if df.empty:
            return None
        
        # Calculate class statistics
        class_stats = df.groupby('student__student_class__name')['score'].agg([
            'mean', 'min', 'max', 'count'
        ]).round(2)
        
        # Create box plot
        fig = px.box(
            df,
            x='student__student_class__name',
            y='score',
            title='Class-wise Score Distribution',
            labels={
                'student__student_class__name': 'Class',
                'score': 'Score'
            }
        )
        
        return fig.to_html(full_html=False)
        
    except Exception as e:
        logger.error(f"Error in class_wise_analysis: {e}", exc_info=True)
        return None

def get_top_performers(marks):
    """Get top performers by subject and overall"""
    try:
        # Convert queryset to DataFrame
        df = pd.DataFrame(list(marks.values(
            'student__full_name', 'score', 'subject__name'
        )))
        
        if df.empty:
            return None, None
        
        # Get top performers by subject
        subject_toppers = df.loc[df.groupby('subject__name')['score'].idxmax()]
        subject_toppers = subject_toppers.to_dict('records')
        
        # Get overall top performers
        student_avg = df.groupby('student__full_name')['score'].mean()
        top_5 = student_avg.nlargest(5)
        overall_toppers = [
            {'student': student, 'average_score': score}
            for student, score in top_5.items()
        ]
        
        return subject_toppers, overall_toppers
        
    except Exception as e:
        logger.error(f"Error in get_top_performers: {e}", exc_info=True)
        return None, None

def generate_student_report(marks):
    """Generate detailed report for a student"""
    try:
        # Convert queryset to DataFrame
        df = pd.DataFrame(list(marks.values(
            'subject__name', 'score', 'exam_date__date_of_exam'
        )))
        
        if df.empty:
            return None
        
        # Calculate statistics
        stats = {
            'total_marks': df['score'].sum(),
            'average_score': df['score'].mean().round(2),
            'highest_score': df['score'].max(),
            'lowest_score': df['score'].min(),
            'subjects_count': len(df['subject__name'].unique()),
            'exams_count': len(df['exam_date__date_of_exam'].unique())
        }
        
        # Create performance trend
        fig = px.line(
            df.sort_values('exam_date__date_of_exam'),
            x='exam_date__date_of_exam',
            y='score',
            title='Performance Trend',
            labels={
                'exam_date__date_of_exam': 'Exam Date',
                'score': 'Score'
            }
        )
        
        stats['trend_plot'] = fig.to_html(full_html=False)
        return stats
        
    except Exception as e:
        logger.error(f"Error in generate_student_report: {e}", exc_info=True)
        return None 