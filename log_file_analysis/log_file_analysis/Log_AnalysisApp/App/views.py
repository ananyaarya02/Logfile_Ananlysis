import advertools as adv
import pandas as pd
from ua_parser import user_agent_parser
import pyarrow.parquet as pq
import pyarrow
import ua_parser
from django.shortcuts import render
from django.shortcuts import render, redirect
from .form import LogFileForm
import matplotlib.pyplot as plt
import io
import base64
from django.http import HttpResponse

# Create your views here.
def index(request):
    print("homne page")
    return render(request, 'App/index.html')

def upload_file(request):
    print("result page")
    if request.method == 'POST':
        form = LogFileForm(request.POST, request.FILES)
        if form.is_valid():
            log_file = request.FILES['log_file']
            analysis_options = form.cleaned_data.get('analysis_option')
        try:
            # Check if the uploaded file is in text format
            if log_file.name.endswith('.txt'):
                # File is in text format, convert it to CSV
                converted_file = convert_to_csv(log_file)
            else:
                # File is already in CSV format
                 converted_file = pd.read_csv(log_file)

            # Now perform analysis based on the converted file
            combined_results = []
            for option in analysis_options:
                for option in analysis_options:
                 if option == "first10 ":
                    result=first_log(converted_file)
                    combined_results.append(result)
                 elif option == "shape":
                     result = shape_log(converted_file)
                     combined_results.append(result)
                 elif option == "top_10_hours":
                     top_hours, plot_data = perform_hourly_analysis(converted_file)
                     combined_results.append(top_hours)
                     combined_results.append(plot_data)
                 elif option=="code_count":
                     result=perform_code_count(converted_file)
                     combined_results.append(result)
                 elif option =="max_hit":
                     result=perform_max_url_hits(converted_file)
                     combined_results.append(result)
                 elif option =='platform_hit':
                      result=perfrom_platform_hit_counts(converted_file)
                      combined_results.append(result)
                 elif option == "browser_hits":
                     result=perform_browser_hits(converted_file)
                     combined_results.append(result)
                 elif option == "trafic_distribution_hourly":
                     result=traffic_distribution_per_hour(converted_file)
                     combined_results.append(result)
                 elif option == "hits_pr_hours":
                     result=perform_hits_per_hour(converted_file)
                     combined_results.append(result)

                
            
                 


            return render(request, 'App/result.html', {'combined_results': combined_results})
        except Exception as e:
                print(f"An error occurred: {e}")
                # Handle error, maybe log it and inform the user
                return HttpResponse("An error occurred during analysis. Please try again or contact support.")
        else:
            # Handle form validation errors
            # You might want to inform the user about form validation errors
            return HttpResponse("Form data is invalid. Please check the form and try again.")
    else:
        print("here")
        form = LogFileForm()
        return render(request, 'App/upload_file.html', {'form': form})

def convert_to_csv(log_file):
  try:
    
    adv.logs_to_df(
       log_file='log_file.log',
       output_file='output_file.parquet',
       errors_file='errors_file.txt',
       log_format='combined')
    converted_file = pd.read_parquet('output_file.parquet')
    if 'datetime' in converted_file.columns:
            converted_file['datetime'] = pd.to_datetime(converted_file['datetime'], format='%d/%b/%Y:%H:%M:%S %z', utc=True)
            converted_file['hour'] = converted_file['datetime'].dt.hour
            converted_file['datetime'] = pd.to_datetime(converted_file['datetime'])
    else:
            print("No 'datetime' column found in the DataFrame.")
        
    return converted_file
  except Exception as e:
        print(f"An error occurred: {e}")
        return None 
   

    


def perform_hourly_analysis(converted_file):
     if 'datetime' in converted_file.columns:
        try:
            converted_file['datetime'] = pd.to_datetime(converted_file['datetime'], format='%d/%b/%Y:%H:%M:%S %z', utc=True)
            converted_file['hour'] = converted_file['datetime'].dt.hour
            top_hours = converted_file['hour'].value_counts().head(10)
    
            plt.bar(top_hours.index, top_hours.values)
            plt.xlabel('Hour')
            plt.ylabel('Number of Hits')
            plt.title('Top 10 Hours for Hits')
    
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()

            return top_hours, plot_data
        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None  # Return placeholders or handle appropriately
     else:
        print("No 'datetime' column found in the DataFrame.")
        return None, None 
def first_log(converted_file):
    top10 =converted_file.head(10)
    return top10

def shape_log(converted_file):
    shape = converted_file.shape
    return shape
def perform_code_count(converted_file):
    http_code_counts =converted_file['status'].value_counts()
    return http_code_counts

def perform_max_url_hits (converted_file):
    url_hit_counts = converted_file['referer'].value_counts()
    max_hit_url = url_hit_counts.idxmax()
    return max_hit_url

def perfrom_platform_hit_counts(converted_file):
    converted_file['platform'] = converted_file['user_agent'].str.extract(r'\((.*?)\)')[0].str.split(';').str[0]
    platform_hit_counts = converted_file['platform'].value_counts()
    return platform_hit_counts

def perform_browser_hits(converted_file):
    converted_file['browser'] = converted_file['user_agent'].str.split('(', n=1, expand=True)[0]
    browser_hit_counts = converted_file['browser'].value_counts()
    return browser_hit_counts

def traffic_distribution_per_hour(converted_file):
    converted_file['data_size'] = converted_file['size'].fillna(0).astype(int)
    data_size_per_hour = converted_file.groupby('hour')['data_size'].sum() / len(converted_file['hour'].unique())  
    return data_size_per_hour


def perform_hits_per_hour(converted_file):
    hits_per_hour_desc = converted_file['hour'].value_counts().sort_index(ascending=False)
    return hits_per_hour_desc

