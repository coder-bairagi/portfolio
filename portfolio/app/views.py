from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from data_science.movie_recommendation_system import mrs
from data_science.property_price_prediction import ppp
from data_science.olympic_data_analysis import plotly_app

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def send_email(request):
    if request.method == 'POST':
        try:
            # Extract form data
            from_email = request.POST.get('from_email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            validation_message = []
            if from_email == '':
                validation_message.append('Email is Required')
            if subject == '':
                validation_message.append('Subject is Required')
            if not message:
                validation_message.append('Message Body is Required')
            if validation_message:
                error_message = ''
                flag = 0
                for val_msg in validation_message:
                    if flag != 0:
                        val_msg = '. ' + val_msg
                    error_message += val_msg
                    flag += 1
                return JsonResponse({'error': error_message}, status=400)
        
            # Email account credentials
            to_password = "jata tsyb lteq rcdo"
            to_email = "anandbairagi500@gmail.com"


            # Create the email content
            subject = "My Website: " + subject
            body = f"New Contact Form Submission:\n\nEmail: {from_email}\nMessage: {message}"

            # Set up the MIME
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach the body with the msg instance
            msg.attach(MIMEText(body, 'plain'))

            # Create the server connection
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(to_email, to_password)

            # Send the email
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)

            # Disconnect from the server
            server.quit()
            return JsonResponse({'message': message})
        except Exception as e:
            # Handle unknown errors
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

# Projects
def projects(request):
    return render(request, 'projects\index.html')
#  Movie recommendation system
def mrs_index(request):
    data = {
        'movies': mrs.movies_list['title'].values
    }
    return render(request, 'projects\movie-recommendation-system\index.html', data)

def get_recommendations(request):
    if request.method == 'POST':
        try:
            selected_movie_name = request.POST.get('movie')
            recommendations = mrs.recommend(selected_movie_name)
            return JsonResponse({'recommendations': recommendations})
        except TimeoutError:
            # Handle connection time out error
            return JsonResponse({'error': 'Connection to TMDB database timed out. Check your network and try again.'}, status=504)
        except Exception as e:
            # Handle unknown errors
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def get_movie_details(request, movie_name):
    base_url = request.build_absolute_uri('/')[:-1]
    movie_id = mrs.get_tmdb_movie_id(movie_name)
    data = mrs.fetch_details(base_url, movie_id, movie_name)
    return render(request, 'projects\movie-recommendation-system\details.html', data)
# Olympic data analysis
def oda_index(request):
    return render(request, 'projects\olympic-data-analysis\index.html')
# Property price prediction
def ppp_index(request):
    data = ppp.get_requirements()
    return render(request, 'projects\property-price-prediction\index.html', data)
def get_price(request):
    if request.method == 'POST':
        try:
            location = request.POST.get('location')
            total_sqft = request.POST.get('total_sqft')
            bath = request.POST.get('bath')
            bhk = request.POST.get('bhk')
            price, shorthand_price = ppp.get_predicted_price(location, total_sqft, bath, bhk)
            return JsonResponse({'price': price, 'shorthand_price': shorthand_price})
        except Exception as e:
            # Handle unknown errors
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


