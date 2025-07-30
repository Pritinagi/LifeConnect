from django.shortcuts import render, redirect

def home(request):
   return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


from .models import Cause

def causes(request):
    all_causes = Cause.objects.all()
    return render(request, 'causes.html', {'causes': all_causes})

from .forms import ContactForm

def contact(request):
    form = ContactForm()
    success = False

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True

    return render(request, 'contact.html', {'form': form, 'success': success})

from django.conf import settings
from django.shortcuts import render, redirect
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
from .forms import DonationForm
from .models import Donation

def donate(request):
    if request.method == "POST":
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.status = "pending"
            donation.save()

            # Save the donation ID in session to update after payment
            request.session['donation_id'] = donation.id

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': f"Donation by {donation.name or donation.email}",
                        },
                        'unit_amount': int(donation.amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:8000/success/',
                cancel_url='http://localhost:8000/cancel/',
            )

            # Optional: Save the session ID or stripe_payment_id
            donation.stripe_payment_id = session.id
            donation.save()

            return redirect(session.url, code=303)
    else:
        form = DonationForm()

    context = {'form': form, 'stripe_pub_key': settings.STRIPE_PUBLISHABLE_KEY}
    return render(request, 'donate.html', context)


def success(request):
    donation_id = request.session.get('donation_id')
    if donation_id:
        donation = Donation.objects.get(id=donation_id)
        donation.status = "success"
        donation.save()
        del request.session['donation_id']  # cleanup

    return render(request, "success.html")

def cancel(request):
    return render(request, "cancel.html")
