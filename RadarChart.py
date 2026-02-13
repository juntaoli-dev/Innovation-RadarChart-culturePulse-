"""
Culture Pulse Radar Chart Visualization
Aggregates all cultural categories and creates an interactive radar chart
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
import sys
import os
from datetime import datetime, timedelta

# Add DataPull directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'DataPull'))

from DataPull.SportsData import SportsDataPuller
from DataPull.PoliticsData import PoliticsDataPuller
from DataPull.TechData import TechDataPuller
from DataPull.EconomyData import EconomyDataPuller
from DataPull.TrendsData import TrendsDataPuller
from DataPull.EntertainmentData import EntertainmentDataPuller
from DataPull.HealthData import HealthDataPuller
from DataPull.EnvironmentData import EnvironmentDataPuller


class CulturePulseRadarChart:
    """Creates and displays a radar chart of cultural pulse across categories"""
    
    def __init__(self):
        self.categories = []
        self.scores = []
    
    def collect_all_data(self, days_back: int = 7, end_date: str = None, start_date: str = None) -> List[Dict]:
        """
        Collect pulse data from all categories
        
        Args:
            days_back: Number of days to look back (ignored if start/end dates provided)
            end_date: End date in format 'YYYY-MM-DD' (optional)
            start_date: Start date in format 'YYYY-MM-DD' (optional)
        """
        if start_date and end_date:
            print(f"🔄 Collecting data from {start_date} to {end_date}...")
        elif end_date:
            print(f"🔄 Collecting data ending on {end_date} (last {days_back} days)...")
        else:
            print(f"🔄 Collecting data for last {days_back} days...")
        print("=" * 60)
        
        pullers = [
            ('Sports', SportsDataPuller()),
            ('Politics', PoliticsDataPuller()),
            ('Tech/Science', TechDataPuller()),
            ('Economy', EconomyDataPuller()),
            ('Trends', TrendsDataPuller()),
            ('Entertainment', EntertainmentDataPuller()),
            ('Health', HealthDataPuller()),
            ('Environment', EnvironmentDataPuller()),
        ]
        
        all_data = []
        
        for category, puller in pullers:
            try:
                print(f"📊 Fetching {category}...", end=" ")
                
                # Get pulse data based on category
                if category == 'Sports':
                    data = puller.get_sports_pulse(days_back, start_date, end_date)
                elif category == 'Politics':
                    data = puller.get_politics_pulse(days_back)
                elif category == 'Tech/Science':
                    data = puller.get_tech_pulse(days_back)
                elif category == 'Economy':
                    data = puller.get_economy_pulse(days_back)
                elif category == 'Trends':
                    data = puller.get_trends_pulse(days_back)
                elif category == 'Entertainment':
                    data = puller.get_entertainment_pulse(days_back)
                elif category == 'Health':
                    data = puller.get_health_pulse(days_back)
                elif category == 'Environment':
                    data = puller.get_environment_pulse(days_back)
                
                all_data.append(data)
                print(f"✅ Score: {data['pulse_score']}/100")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                # Add placeholder data if fetch fails
                all_data.append({
                    'category': category,
                    'pulse_score': 0,
                    'article_count': 0,
                    'total_results': 0
                })
        
        print("=" * 60)
        return all_data
    
    def normalize_scores_relative(self, data: List[Dict]) -> List[Dict]:
        """
        Normalize scores relative to each other - makes differences DRAMATIC
        The highest scorer gets boosted, others get suppressed
        This shows which category is DOMINATING the culture
        """
        if not data:
            return data
        
        scores = [d['pulse_score'] for d in data]
        max_score = max(scores)
        min_score = min(scores)
        avg_score = np.mean(scores)
        
        normalized_data = []
        for d in data:
            original_score = d['pulse_score']
            
            # If score is above average, boost it exponentially
            # If below average, suppress it
            if original_score >= avg_score:
                # Boost high performers
                boost_factor = 1 + ((original_score - avg_score) / avg_score) * 2
                new_score = min(100, original_score * boost_factor)
            else:
                # Suppress low performers
                suppress_factor = original_score / avg_score
                new_score = original_score * suppress_factor * 0.8
            
            normalized_data.append({
                **d,
                'pulse_score': round(new_score, 2),
                'original_score': original_score
            })
        
        return normalized_data
    
    def create_radar_chart(self, data: List[Dict], save_path: str = None, title_suffix: str = ""):
        """
        Create and display radar chart visualization
        
        Args:
            data: List of pulse data dictionaries
            save_path: Optional path to save the chart image
            title_suffix: Additional text for title
        """
        # Extract categories and scores
        self.categories = [d['category'] for d in data]
        self.scores = [d['pulse_score'] for d in data]
        
        # Number of variables
        num_vars = len(self.categories)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        
        # Complete the circle
        self.scores += self.scores[:1]
        angles += angles[:1]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Draw the outline of our data
        ax.plot(angles, self.scores, 'o-', linewidth=2, label='Culture Pulse', color='#FF6B6B')
        ax.fill(angles, self.scores, alpha=0.25, color='#FF6B6B')
        
        # Fix axis to go from 0 to 100
        ax.set_ylim(0, 100)
        
        # Draw ytick labels
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], color='grey', size=10)
        
        # Draw xtick labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.categories, size=12, weight='bold')
        
        # Add title
        main_title = 'Culture Pulse Radar Chart'
        if title_suffix:
            main_title += f'\n{title_suffix}'
        else:
            main_title += '\nReal-Time Cultural Engagement Across Categories'
        plt.title(main_title, size=16, weight='bold', pad=20)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.figtext(0.5, 0.02, f'Generated: {timestamp}', ha='center', size=10, style='italic')
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n💾 Chart saved to: {save_path}")
        
        # Display
        plt.tight_layout()
        plt.show()
        
    def create_comparison_chart(self, datasets: List[Tuple[str, List[Dict]]], save_path: str = None):
        """
        Create radar chart comparing multiple time periods
        
        Args:
            datasets: List of tuples (label, data) for each time period
            save_path: Optional path to save the chart image
        """
        # Use first dataset for categories
        self.categories = [d['category'] for d in datasets[0][1]]
        num_vars = len(self.categories)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10), subplot_kw=dict(projection='polar'))
        
        # Color palette for different time periods
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        # Plot each dataset
        for i, (label, data) in enumerate(datasets):
            scores = [d['pulse_score'] for d in data]
            scores += scores[:1]  # Complete the circle
            
            color = colors[i % len(colors)]
            ax.plot(angles, scores, 'o-', linewidth=2, label=label, color=color)
            ax.fill(angles, scores, alpha=0.15, color=color)
        
        # Fix axis to go from 0 to 100
        ax.set_ylim(0, 100)
        
        # Draw ytick labels
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], color='grey', size=10)
        
        # Draw xtick labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.categories, size=12, weight='bold')
        
        # Add title
        plt.title('Culture Pulse Comparison\nMulti-Period Analysis', 
                  size=16, weight='bold', pad=20)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        plt.figtext(0.5, 0.02, f'Generated: {timestamp}', ha='center', size=10, style='italic')
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n💾 Comparison chart saved to: {save_path}")
        
        # Display
        plt.tight_layout()
        plt.show()
        
    def print_summary(self, data: List[Dict]):
        """Print a text summary of the culture pulse"""
        print("\n📊 CULTURE PULSE SUMMARY")
        print("=" * 60)
        
        sorted_data = sorted(data, key=lambda x: x['pulse_score'], reverse=True)
        
        for i, d in enumerate(sorted_data, 1):
            category = d['category']
            score = d['pulse_score']
            articles = d['article_count']
            
            # Determine engagement level
            if score >= 70:
                level = "🔥 HIGH"
            elif score >= 40:
                level = "📈 MEDIUM"
            else:
                level = "📉 LOW"
            
            print(f"{i}. {category:15} | {level:12} | Score: {score:5.1f}/100 | Articles: {articles:3}")
        
        print("=" * 60)
        
        # Calculate average
        avg_score = np.mean([d['pulse_score'] for d in data])
        print(f"\n🌐 Overall Cultural Pulse: {avg_score:.1f}/100")
        print()


def interactive_menu():
    """Interactive menu for selecting time periods"""
    print("\n" + "=" * 70)
    print("🌍 CULTURE PULSE RADAR CHART GENERATOR")
    print("=" * 70 + "\n")
    
    print("Select mode:")
    print("1. Current Pulse (last 7 days)")
    print("2. Custom Date Range")
    print("3. Compare Multiple Time Periods")
    print("4. Historical Comparison (Last 7, 14, 30 days)")
    print("5. Specific Date (e.g., Super Bowl Day)")
    print()
    5
    choice = input("Enter choice (1-4): ").strip()
    
    radar = CulturePulseRadarChart()
    
    if choice == "1":
        # Current pulse
        print("\n📊 Analyzing current culture pulse...")
        pulse_data = radar.collect_all_data(days_back=7)
        pulse_data = radar.normalize_scores_relative(pulse_data)  # Make differences dramatic
        radar.print_summary(pulse_data)
        print("📊 Generating radar chart...")
        radar.create_radar_chart(pulse_data, save_path='culture_pulse_radar.png')
        
    elif choice == "2":
        # Custom date range
        days = input("\nEnter number of days to analyze (default 7): ").strip()
        days = int(days) if days else 7
        
        pulse_data = radar.normalize_scores_relative(pulse_data)  # Make differences dramatic
        pulse_data = radar.collect_all_data(days_back=days)
        radar.print_summary(pulse_data)
        print("📊 Generating radar chart...")
        radar.create_radar_chart(
            pulse_data, 
            save_path=f'culture_pulse_{days}days.png',
            title_suffix=f'Last {days} Days Analysis'
        )
        
    elif choice == "3":
        # Compare multiple periods
        print("\n📊 Multi-Period Comparison")
        num_periods = input("How many time periods to compare? (2-5): ").strip()
        num_periods = min(5, max(2, int(num_periods) if num_periods else 2))
        
        datasets = []
        for i in range(num_periods):
            print(f"\n--- Period {i+1} ---")
            days = input(f"Days back for period {i+1} (e.g., 7, 14, 30): ").strip()
            days = int(days) if days else 7 * (i + 1)
            
            label = input(f"Label for period {i+1} (default: 'Last {days} days'): ").strip()
            label = label if label else f"Last {days} days"
            
            print(f"Collecting data for {label}...")
            data = radar.normalize_scores_relative(data)  # Make differences dramatic
            data = radar.collect_all_data(days_back=days)
            datasets.append((label, data))
        
        print("\n📊 Generating comparison chart...")
        radar.create_comparison_chart(datasets, save_path='culture_pulse_comparison.png')
        
    elif choice == "4":
        # Historical comparison (preset)
        print("\n📊 Historical Comparison: 7, 14, and 30 days")
        
        datasets = []
        for days, label in [(7, "Last Week"), (14, "Last 2 Weeks"), (30, "Last Month")]:
            prin = radar.normalize_scores_relative(data)  # Make differences dramatic
            datat(f"\nCollecting {label} data...")
            data = radar.collect_all_data(days_back=days)
            datasets.append((label, data))
            
            # Print quick summary
            avg_score = np.mean([d['pulse_score'] for d in data])
            print(f"  → Average pulse: {avg_score:.1f}/100")
        
        print("\n📊 Generating comparison chart...")
        radar.create_comparison_chart(datasets, save_path='culture_pulse_historical.png')
        
        # Print detailed summaries
        for label, data in datasets:
            print(f"\n{'='*70}")
            print(f"📊 {label.upper()}")
            print('='*70)
            radar.print_summary(data)
    
    elif choice == "5":
        # Specific single date
        print("\n📊 Specific Date Analysis")
        print("\n💡 Quick options:")
        print("  1. Super Bowl Day (Feb 9, 2026)")
        print("  2. Custom date")
        
        date_choice = input("\nChoose (1-2): ").strip()
        
        if date_choice == "1":
            # Super Bowl Day - February 9, 2026
            specific_date = "2026-02-09"
            label = "Super Bowl Sunday"
        else:
            specific_date = input("Enter date (YYYY-MM-DD): ").strip()
            label = f"Date: {specific_date}"
        
        # Analyze just that one day
        print(f"\n🔥 Analyzing {label}...")
        pulse_data = radar.collect_all_data(
            days_back=1, 
            start_date=specific_date, 
            end_date=specific_date
        )
        pulse_data = radar.normalize_scores_relative(pulse_data)  # Make differences SUPER dramatic
        radar.print_summary(pulse_data)
        
        print(f"📊 Generating radar chart for {label}...")
        safe_filename = specific_date.replace('-', '')
        radar.create_radar_chart(
            pulse_data,
            save_path=f'culture_pulse_{safe_filename}.png',
            title_suffix=f'{label}'
        )
    
    else:
        print("❌ Invalid choice!")
        return
    
    print("\n✅ Culture Pulse Analysis Complete!")
    print("=" * 70 + "\n")


def main():
    """Main execution function"""
    interactive_menu()


if __name__ == "__main__":
    main()
