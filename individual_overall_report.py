# This script generates indivudal reports that summarize data collection since the beginning of the study. It includes ALL time points


import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import datetime as dtm
from datetime import datetime, timedelta
from matplotlib.lines import Line2D
import statistics
from matplotlib import rcParams

pd.set_option('display.max_rows', None)

# Set the font globally
# rcParams['font.family'] = 'Roboto'

# LOAD DATA

# Define a function to add a separator in the legend
def add_legend_separator():
    handles.append(Line2D([0], [0], color='white', lw=0))  # Adds a blank line as separator
    labels.append('')

# Define the path to the folder containing the CSV files
sleep_data_folder_path = r'C:\Users\dylan\OneDrive - McGill University\McPsyt Lab Douglas\actigraphy\sleep_data'
activity_data_folder_path = r'C:\Users\dylan\OneDrive - McGill University\McPsyt Lab Douglas\actigraphy\activity_data'

# List all CSV files in the folder
sleep_files = [file for file in os.listdir(sleep_data_folder_path) if file.endswith('.csv')]
activity_files = [file for file in os.listdir(activity_data_folder_path) if file.endswith('.csv')]

sleep_data = {}
activity_data = {}
list_of_IDs = []

# Transfer files into dictionnary and create a list of IDs
for sleep_file in sleep_files:
    sleep_file_name = os.path.splitext(sleep_file)[0]
    if sleep_file_name[:3] not in list_of_IDs:
        list_of_IDs.append(sleep_file_name[:3])
    sleep_data[sleep_file_name] = pd.read_csv(os.path.join(sleep_data_folder_path, sleep_file))

for activity_file in activity_files:
    activity_file_name = os.path.splitext(activity_file)[0]
    activity_data[activity_file_name] = pd.read_csv(os.path.join(activity_data_folder_path, activity_file))



for participant_id in list_of_IDs:

    print(f'PROCESSING PARTICIPANT DD_{participant_id}')
    mean_onset_list = []
    mean_rise_list = []
    sleep_individual_dataframes = []
    sleep_individual_dataframes_names = []
    activity_individual_dataframes = []
    activity_individual_dataframes_names = []

    # Add DataFrames from sleep_data
    for sleep_file_name, df in sleep_data.items():
        if f'{participant_id}' in sleep_file_name:
            sleep_individual_dataframes.append(df)
            sleep_individual_dataframes_names.append(sleep_file_name)
        
    # Add DataFrames from activity_data
    for activity_file_name, df in activity_data.items():
        if f'{participant_id}' in activity_file_name:
            activity_individual_dataframes.append(df)
            activity_individual_dataframes_names.append(activity_file_name)

    if sleep_individual_dataframes and activity_individual_dataframes:
        
        sleep_df = sleep_individual_dataframes[0]
        sleep_df['Sleep.Onset.Time'] = pd.to_datetime(sleep_df['Sleep.Onset.Time'], format='%H:%M', errors='coerce')
        sleep_df['Rise.Time'] = pd.to_datetime(sleep_df['Rise.Time'], format='%H:%M', errors='coerce')
        mean_onset = sleep_df.loc[sleep_df['Night.Starting'] == 'Mean', 'Sleep.Onset.Time'].iloc[0]
        mean_rise = sleep_df.loc[sleep_df['Night.Starting'] == 'Mean', 'Rise.Time'].iloc[0]
        mean_onset_list.append(mean_onset)
        mean_rise_list.append(mean_rise)
        sleep_df = sleep_df[sleep_df['Night.Starting'] != 'Mean']
        sleep_df = sleep_df[(sleep_df == 0).sum(axis=1) < 5]
        sleep_df['Night.Starting'] = pd.to_datetime(sleep_df['Night.Starting'])

        activity_df = activity_individual_dataframes[0]
        # Create a Date column for activity_df based on the dates in the corresponding sleep_df
        activity_df['Date'] = pd.concat([pd.Series(sleep_df['Night.Starting'].iloc[0] - pd.Timedelta(days=1)), sleep_df['Night.Starting']]).reset_index(drop=True)
        activity_df['Date'] = pd.to_datetime(activity_df['Date'])
        activity_df = activity_df[(activity_df==0).sum(axis=1) < 5]

        for i in range(1, len(sleep_individual_dataframes)):
            sleep_individual_dataframes[i]['Sleep.Onset.Time'] = pd.to_datetime(sleep_individual_dataframes[i]['Sleep.Onset.Time'], format='%H:%M', errors='coerce')
            sleep_individual_dataframes[i]['Rise.Time'] = pd.to_datetime(sleep_individual_dataframes[i]['Rise.Time'], format='%H:%M', errors='coerce')
            mean_onset = sleep_individual_dataframes[i].loc[sleep_individual_dataframes[i]['Night.Starting'] == 'Mean', 'Sleep.Onset.Time'].iloc[0]
            mean_rise = sleep_individual_dataframes[i].loc[sleep_individual_dataframes[i]['Night.Starting'] == 'Mean', 'Rise.Time'].iloc[0]
            mean_onset_list.append(mean_onset)
            mean_rise_list.append(mean_rise)
            sleep_individual_dataframes[i] = sleep_individual_dataframes[i][sleep_individual_dataframes[i]['Night.Starting'] != 'Mean']
            sleep_individual_dataframes[i] = sleep_individual_dataframes[i][(sleep_individual_dataframes[i] == 0).sum(axis=1) < 5]

            if len(sleep_individual_dataframes) > 1:
                sleep_df = pd.concat([sleep_df, sleep_individual_dataframes[i]], ignore_index=True)
            
        for i in range(1, len(activity_individual_dataframes)):

            if len(activity_individual_dataframes) > 1:
                # Create a Date column for activity_df based on the dates in the corresponding sleep_df
                sleep_individual_dataframes[i]['Night.Starting'] = pd.to_datetime(sleep_individual_dataframes[i]['Night.Starting'])
                activity_individual_dataframes[i]['Date'] = pd.concat([pd.Series(sleep_individual_dataframes[i]['Night.Starting'].iloc[0] - pd.Timedelta(days=1)), sleep_individual_dataframes[i]['Night.Starting']]).reset_index(drop=True)
                activity_individual_dataframes[i]['Date'] = pd.to_datetime( activity_individual_dataframes[i]['Date'])

                activity_individual_dataframes[i] = activity_individual_dataframes[i][(activity_individual_dataframes[i] == 0).sum(axis=1) < 5]
                activity_df = pd.concat([activity_df, activity_individual_dataframes[i]], ignore_index=True)
                
                # Make sure no dates appear twice, and if so take the sum of the columns
                activity_df = activity_df.groupby('Date', as_index=False)[['Steps', 'Non_Wear', 'Sleep', 'Sedentary', 'Light', 'Moderate', 'Vigorous']].sum()



        # Store mean onset time and mean rise time
        onset_seconds = [onset.hour * 3600 + onset.minute * 60 + onset.second for onset in mean_onset_list]
        mean_onset_seconds = sum(onset_seconds) / len(onset_seconds)
        final_mean_onset = pd.Timestamp("2023-10-25").replace(second=0) + pd.to_timedelta(mean_onset_seconds, unit='s')

        rise_seconds = [rise.hour * 3600 + rise.minute * 60 + rise.second for rise in mean_rise_list]
        mean_rise_seconds = sum(rise_seconds) / len(rise_seconds)
        final_mean_rise = pd.Timestamp("2023-10-25").replace(second=0) + pd.to_timedelta(mean_rise_seconds, unit='s')

        print('debug')
        print(mean_onset_list)
        print(final_mean_onset)
        print(mean_rise_list)
        print(final_mean_rise)
        

        # Set a specific date (12-10-2003) for both times
        arbitrary_date = datetime.strptime('12-10-2003', '%d-%m-%Y')
        sleep_df['Sleep.Onset.Time'] = sleep_df['Sleep.Onset.Time'].apply(lambda x: x.replace(year=arbitrary_date.year, month=arbitrary_date.month, day=arbitrary_date.day) if pd.notnull(x) else x)
        sleep_df['Rise.Time'] = sleep_df['Rise.Time'].apply(lambda x: x.replace(year=arbitrary_date.year, month=arbitrary_date.month, day=arbitrary_date.day) if pd.notnull(x) else x)

        def adjust_sleep_time(row, date_comparator):
            time = row.time()
            if time < pd.Timestamp('06:00').time() and date_comparator.date() == pd.Timestamp('2003-10-12').date():
                return (date_comparator + pd.Timedelta(days=1)).replace(hour=time.hour, minute=time.minute)
            
            return date_comparator.replace(hour=time.hour, minute=time.minute)

        date_comparator = pd.Timestamp('2003-10-12 06:00')

        # Apply the adjustment to Sleep Time Onset and Rise Time columns
        sleep_df['Sleep.Onset.Time'] = sleep_df['Sleep.Onset.Time'].apply(lambda x: adjust_sleep_time(x, date_comparator))
        sleep_df['Rise.Time'] = sleep_df['Rise.Time'].apply(lambda x: adjust_sleep_time(x, date_comparator))

        onset_variability = sleep_df['Sleep.Onset.Time'].diff().abs().dt.total_seconds().mean() / 3600  # Convert to hours
        rise_variability = sleep_df['Rise.Time'].diff().abs().dt.total_seconds().mean() / 3600  # Convert to hours
        print(onset_variability)
        print(rise_variability)


        # Remove rows with earliest and latest date, as they are incomplete
        # For earliest date, they picked up the watch during the day, so it's not a full day of data
        # For latest date, they are giving back the watch, so it's not a full day of data
        earliest_date = activity_df['Date'].min()
        latest_date = activity_df['Date'].max()
        print(f'The date {earliest_date} has been removed for participant DD_{participant_id}')
        print(f'The date {latest_date} has been removed for participant DD_{participant_id}')
        activity_df = activity_df[activity_df['Date'] != earliest_date]
        activity_df = activity_df[activity_df['Date'] != latest_date]

        # Convert into datetimes again (i know we did it earlier but it seems that it's still strings, so let's just do it again on the contatenated dataframes)
        sleep_df['Night.Starting'] = pd.to_datetime(sleep_df['Night.Starting'])
        activity_df['Date'] = pd.to_datetime(activity_df['Date'])

        min_date = min(sleep_df['Night.Starting'].min(), activity_df['Date'].min())
        max_date = max(sleep_df['Night.Starting'].max(), activity_df['Date'].max())

        print(f'Min date: {min_date}')
        print(f'Max date: {max_date}')


        # Convert sleep time to hours
        sleep_df['Total.Sleep.Time'] = sleep_df['Total.Sleep.Time'] / 3600

        # Calculate sleep duration variability
        sleep_df['Sleep.Difference'] = sleep_df['Total.Sleep.Time'].diff()
        sleep_variability = sleep_df['Sleep.Difference'].abs().mean()

        # Create a date range for x-ticks from min_date - 1 day to max_date + 1 day
        daily_date_range = pd.date_range(start=min_date - pd.Timedelta(days=1), end=max_date + pd.Timedelta(days=1), freq='D')
        weekly_date_range = pd.date_range(start=min_date - pd.Timedelta(days=1), end=max_date + pd.Timedelta(days=1), freq='W')

        # Define x-limits
        x_limits = (min_date - pd.Timedelta(days=1), max_date + pd.Timedelta(days=1))










########################### PLOTTING


        # Adjusted Code for Consolidated Legend with Sections
        fig, axes = plt.subplots(2, 2, figsize=(24, 14), sharex=True)

        # Define lists to store legend handles and labels
        handles, labels = [], []

        # Total Sleep Time
        axes[0, 0].plot(sleep_df['Night.Starting'], sleep_df['Total.Sleep.Time'], label='Sleep', color='#5D3A9B', marker='o', markersize=5)
        avg_sleep = sleep_df['Total.Sleep.Time'].mean()
        axes[0, 0].axhline(avg_sleep, linestyle='--', color='#5D3A9B', label=f'Avg Sleep: {avg_sleep:.2f} hrs')
        axes[0, 0].set_ylabel('Time (Hours)')
        axes[0, 0].set_title('Sleep', fontsize=16, fontweight='bold')

        # Collect handles and labels
        h, l = axes[0, 0].get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)

        # Add separator
        add_legend_separator()

        # Sleep Efficiency
        axes[0, 1].plot(sleep_df['Night.Starting'], sleep_df['Sleep.Efficiency'], label='Sleep Efficiency', color='blue', marker='o', markersize=5)
        avg_efficiency = sleep_df['Sleep.Efficiency'].mean()
        axes[0, 1].axhline(avg_efficiency, linestyle='--', color='blue', label=f'Avg Sleep Efficiency: {avg_efficiency:.2f}%')
        axes[0, 1].set_ylabel('Sleep Efficiency (%)')
        axes[0, 1].set_yticks(np.arange(0, 101, 10))
        axes[0, 1].set_title('Sleep Efficiency', fontsize=16, fontweight='bold')

        # Custom legend title with detailed info
        title_text = (f'Daily Sleep Duration Variability: {sleep_variability:.2f} hrs\n'
              f'Mean Sleep Time Onset: {final_mean_onset.strftime("%H:%M:%S")}\n'
              f'Daily Variability Sleep Time Onset: {onset_variability:.2f} hrs\n'
              f'Mean Rise Time: {final_mean_rise.strftime("%H:%M:%S")}\n'
              f'Daily Variability Rise Time: {rise_variability:.2f} hrs')

        # Collect handles and labels
        h, l = axes[0, 1].get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)

        # Add separator
        add_legend_separator()

        # Activity Plot for Sedentary, Light, Moderate, Vigorous
        activity_cols = ['Sedentary', 'Light', 'Moderate', 'Vigorous']
        activity_labels = ['Sedentary Activity', 'Light Physical Activity', 'Moderate Physical Activity', 'Vigorous Physical Activity']
        colors = ['purple', 'green', 'orange', 'pink']  # Colors for each activity type
        activity_df[activity_cols] = activity_df[activity_cols] / 3600  # convert to hours

        for col, label, color in zip(activity_cols, activity_labels, colors):
            axes[1, 0].plot(activity_df['Date'], activity_df[col], label=label, color=color, marker='o', markersize=5)
            avg_value = activity_df[col].mean()
            axes[1, 0].axhline(avg_value, linestyle='--', color=color, label=f'Avg {label}: {avg_value:.2f} hrs')

        axes[1, 0].set_ylabel('Time (Hours)')
        axes[1, 0].set_title('Physical Activity', fontsize=16, fontweight='bold')

        # Collect handles and labels
        h, l = axes[1, 0].get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)

        # Add separator
        add_legend_separator()

        # Steps Plot
        axes[1, 1].plot(activity_df['Date'], activity_df['Steps'], label='Steps', color='#B61826', marker='o', markersize=5)
        avg_steps = activity_df['Steps'].mean()
        axes[1, 1].axhline(avg_steps, linestyle='--', color='#B61826', label=f'Avg Steps: {avg_steps:.0f}')
        axes[1, 1].set_ylabel('Steps')
        axes[1, 1].set_title('Steps', fontsize=16, fontweight='bold')

        # Collect handles and labels
        h, l = axes[1, 1].get_legend_handles_labels()
        handles.extend(h)
        labels.extend(l)

        plt.xlim(x_limits)
        axes[1, 0].set_xticks(ticks=daily_date_range, labels=[d.strftime('%Y-%m-%d') if d in weekly_date_range else '' for d in daily_date_range], rotation=90)
        axes[1, 1].set_xticks(ticks=daily_date_range, labels=[d.strftime('%Y-%m-%d') if d in weekly_date_range else '' for d in daily_date_range], rotation=90)
        axes[1, 0].set_xlabel('Date')
        axes[1, 1].set_xlabel('Date')

        # Create a single, consolidated legend
        fig.legend(handles, labels, loc='center left', bbox_to_anchor=(0, 0.5), title=title_text, title_fontsize=15, fontsize=15, frameon=True)

        # Adjust the top margin to give space for the title
        plt.subplots_adjust(top=0.75)


        # Align the title text with the legend's bbox
        title_x, title_y = 0, 0.95  # Adjust x and y based on the legend's bbox location
        plt.suptitle('Your Complete Results from Actigraphy Data (Watch)', 
             fontsize=50, fontweight='bold', ha='left', x=title_x, y=title_y)
        
        
        # Add an underline using fig.text for precise positioning
        fig.text(0, 0.89, '_' * 63, fontsize=50, color='black', ha='left')

        # Add the subtitle below the main title
        fig.text(0, 0.78, 
                'Information from the watch data since the beginning of the study.\nFrom it, we can track sleep variation, sleep efficiency, physical activity, and steps!\nOnly data from the past month are included in the current progress report.',
                fontsize=25, ha='left')


        


        # Adjust layout
        plt.subplots_adjust(left=0.25, right=0.95)
        plt.savefig(f'../individual_overall_reports/overall_report_DD_{participant_id}.png', dpi=300)