from rest_framework import generics
from .models import *
from .serializers import VoterSerializer
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit  # pip install pdfkit
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from googletrans import Translator
from django.contrib.gis.geoip2 import GeoIP2
from io import BytesIO
from django.http import FileResponse
from googletrans import Translator
from io import BytesIO
from weasyprint import HTML
from django.template.loader import render_to_string
from xhtml2pdf import pisa

translator = Translator()

def translate_data_to_hindi(data):
    hindi_data = {}
    for k, v in data.items():
        if isinstance(v, str):
            try:
                # synchronous translation
                hindi_data[k] = translator.translate(v, dest="hi").text
            except Exception:
                # fallback to original text if translation fails
                hindi_data[k] = v
        else:
            hindi_data[k] = v
    return hindi_data

##CRUD API
#class VoterListCreate (generics.ListCreateAPIView): 
#    queryset = Voter.objects.all() 
#    serializer_class = VoterSerializer
    
#class VoterRetrieveUpdateDelete(generics.RetrieveUpdateDestroyAPIView): 
#    queryset = Voter.objects.all() 
#    serializer_class = VoterSerializer

class VoterCreateAPI(generics.CreateAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer

##===========================================
# Admin Approve voter Registration
##===========================================
class ApproveVoterAPI(APIView):
    def post(self, request, pk):
        try:
            voter = Voter.objects.get(pk=pk)
            voter.is_approved = True
            voter.save()
            return Response({"status": "Approved"})
        except Voter.DoesNotExist:
            return Response({"error": "Voter not found"}, status=404)


class VoterGetAPI(generics.RetrieveAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer

    def retrieve(self, request, *args, **kwargs):
        lang = request.GET.get("lang", "en")

        response = super().retrieve(request, *args, **kwargs)

        # convert fields
        if lang == "hi":
            response.data = translate_data_to_hindi(response.data)

        return response

class VoterUpdateAPI(generics.UpdateAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer

class VoterDeleteAPI(generics.DestroyAPIView):
    queryset = Voter.objects.all()
    serializer_class = VoterSerializer


class VoterSearchAPI(ListAPIView):
    serializer_class = VoterSerializer

    def get_queryset(self):
        qs = Voter.objects.filter(status='active')
        
        constituency = self.request.GET.get("constituency")
        booth = self.request.GET.get("booth")
        phone = self.request.GET.get("phone")
        name = self.request.GET.get("name")
        epic = self.request.GET.get("epic")
        code = self.request.GET.get("code")
        
         # 🔵 Search by constituency
        if constituency:
            qs = qs.filter(constituency__icontains=constituency)

        # 🔵 Search by booth
        if booth:
            qs = qs.filter(booth__icontains=booth)
            
        if phone and name:
            qs = qs.filter(Q(phone__icontains=phone) & Q(name__icontains=name))
        if epic:
            qs = qs.filter(epic_number__icontains=epic)
        if code:
            qs = qs.filter(unique_code__icontains=code)

        return qs

    def list(self, request, *args, **kwargs):
        lang = request.GET.get("lang", "en")

        response = super().list(request, *args, **kwargs)
        if lang == "hi":
            response.data = translate_list_to_hindi(response.data)
        return response

def get_age(dob):
    from datetime import date 
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def generate_voter_pdf(request, voter, lang='en'):
    """
    Generate PDF for a voter using WeasyPrint.
    Logs the download event.
    """
    # Log download
    LoginLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        voter=voter,
        role="Voter",
        ip_address=get_client_ip(request),
        device_info=request.META.get('HTTP_USER_AGENT', ''),
        action=f"Downloaded voter data: {voter.unique_code}",
        login_time=timezone.now()
    )

    # Select template based on language
    template = 'voters/voter_pdf_hi.html' if lang == 'hi' else 'voters/voter_pdf_en.html'

    # Prepare context
    context = {
        'voter': voter,
        'age': get_age(voter.date_of_birth),
        'lang': lang
    }

    html_string = render_to_string(template, context)
    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_file)
    if pisa_status.err:
        raise Exception("PDF generation failed")

    pdf_file.seek(0)
    return pdf_file

class VoterDownloadAPI(APIView):
    def get(self, request, pk):
        lang = request.GET.get("lang", "en")
        fmt = request.GET.get("format", "json")
        epic = request.GET.get('epic')
        phone = request.GET.get('phone')
        
        # Fetch voter
        try:
            if epic:
                voter = Voter.objects.get(epic_number=epic)
            elif phone:
                voter = Voter.objects.get(phone=phone)
            elif pk:
                voter = Voter.objects.get(pk=pk)
                print("voter:",voter)
            else:
                return Response({"error": "No identifier provided"}, status=400)
        except Voter.DoesNotExist:
            return Response({"error": "Voter not found"}, status=404)

        # JSON output
        if fmt == "json":
            data = VoterSerializer(voter).data
            print("data:",data)
            if lang == "hi":
                data = translate_data_to_hindi(data)
                print("lan:",lang)
            return Response(data)

        # PDF output
        elif fmt == "pdf":
            print("PDF branch called")
            try:
                pdf_file = generate_voter_pdf(request, voter, lang=lang)
                print("PDF generated, size:", pdf_file.getbuffer().nbytes)
                return FileResponse(
                    pdf_file,
                    as_attachment=True,
                    filename=f"voter_{voter.epic_number}.pdf",
                    content_type='application/pdf'
                )
            except Exception as e:
                print("PDF generation error:", e)
                return Response({"error": f"PDF generation failed: {e}"}, status=500)
        return Response(status=200)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# PDF Generation (English + Hindi)
#def generate_voter_pdf(request, pk): 
#    voter = Voter.objects.get(pk=pk) 
#    context = {'voter': voter,'age': get_age(voter.date_of_birth)} 
#    html = render_to_string('voters/voter_pdf.html', context) 
#    pdf = pdfkit.from_string(html,False) 
#    response = HttpResponse(pdf, content_type='application/pdf') 
#    response['Content-Disposition'] =f'attachment; filename="voter_{voter.epic_number}.pdf"'
#    return response



import random
from django.core.cache import cache

def request_voter_pdf(request, pk):
    voter = Voter.objects.get(pk=pk)
    otp = random.randint(100000, 999999)
    cache.set(f"voter_otp_{voter.id}", otp, timeout=300)  # 5 min
    # Send OTP via SMS/Email
    print(f"OTP for voter {voter.id}: {otp}")  # Replace with SMS/Email service
    return HttpResponse("OTP sent, verify to download PDF")

def verify_voter_pdf(request, pk):
    voter = Voter.objects.get(pk=pk)
    input_otp = request.POST.get("otp")
    cached_otp = cache.get(f"voter_otp_{voter.id}")
    if input_otp == str(cached_otp):
        # Optional: add Face/Finger scan check via FastAPI ML
        return generate_voter_pdf(request, pk)
    return HttpResponse("OTP Verification Failed")

#import random
#from django.core.cache import cache
#from django.http import HttpResponse
#from django.conf import settings
#from twilio.rest import Client

#from .models import Voter
#from .pdf import generate_voter_pdf  # use your earlier PDF function

#def request_voter_pdf(request, voter_id):
#    """
#    Step 1: Request to generate PDF
#    Sends OTP to voter's phone
#    """
#    voter = Voter.objects.get(id=voter_id)
#    otp = random.randint(100000, 999999)
#    cache.set(f"voter_otp_{voter.id}", otp, timeout=300)  # 5 min expiry

#    # Send SMS via Twilio
#    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#    client.messages.create(
#        body=f"Your OTP for voter PDF download is: {otp}",
#        from_=settings.TWILIO_PHONE_NUMBER,
#        to=voter.phone
#    )

#    return HttpResponse(f"OTP sent to {voter.phone}. Valid for 5 minutes.")

import requests
from django.views.decorators.csrf import csrf_exempt

FASTAPI_URL = "http://127.0.0.1:8001"

@csrf_exempt
def verify_voter_pdf(request, voter_id):
    """
    Step 2: Verify OTP + optional face/fingerprint
    """
    voter = Voter.objects.get(id=voter_id)
    input_otp = request.POST.get("otp")
    cached_otp = cache.get(f"voter_otp_{voter.id}")

    if str(input_otp) != str(cached_otp):
        return HttpResponse("OTP Verification Failed", status=400)

    # Optional: Face verification
    face_file = request.FILES.get("face_image")
    if face_file:
        resp = requests.post(
            f"{FASTAPI_URL}/check_duplicate_face/",
            files={"file": face_file}
        )
        data = resp.json()
        if not data.get("duplicates") or all(d["voter_id"] != voter.id for d in data["duplicates"]):
            return HttpResponse("Face verification failed", status=400)

    # Optional: Fingerprint verification
    fingerprint_file = request.FILES.get("fingerprint")
    if fingerprint_file:
        resp = requests.post(
            f"{FASTAPI_URL}/check_duplicate_fingerprint/",
            files={"file": fingerprint_file}
        )
        data = resp.json()
        if not data.get("match") or data.get("voter_id") != voter.id:
            return HttpResponse("Fingerprint verification failed", status=400)

    # OTP + biometric passed → Generate PDF
    return generate_voter_pdf(request, voter.id)



