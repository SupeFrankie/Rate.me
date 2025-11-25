from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_feedback_notification(feedback):
    """Send email to lecturer when they receive new feedback from students"""
    lecturer = feedback.lecturer
    
    subject = f"New Feedback Received - {feedback.couse.code}"
    
    #HTML content
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h2 style="color: white; text-align: center;">🎓 New Feedback Received!</h2>
        </div>
        
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa;">
            <h3 style="color: #0d6efd;">Hi {lecturer.get_full_name()},</h3>
            
            <p>You've received new feedback for your course <strong>{feedback.course.name} ({feedback.course.code})</strong>.</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h4 style="color: #6a11cb; margin-top: 0;">Feedback Summary</h4>
                <p><strong>Overall Rating:</strong> {feedback.rating}/5 ⭐</p>
                {'<p><strong>Teaching Quality:</strong> ' + str(feedback.teaching_rating) + '/5</p>' if feedback.teaching_rating else ''}
                {'<p><strong>Communication:</strong> ' + str(feedback.communication_rating) + '/5</p>' if feedback.communication_rating else ''}
                {'<p><strong>Engagement:</strong> ' + str(feedback.engagement_rating) + '/5</p>' if feedback.engagement_rating else ''}
                
                {f'<div style="background: #f0f4ff; padding: 15px; border-left: 4px solid #0d6efd; margin-top: 15px;"><p style="margin: 0;"><em>"{feedback.comment}"</em></p></div>' if feedback.comment else ''}
            </div>
            
            <p style="text-align: center;">
                <a href="{settings.ALLOWED_HOSTS[0]}/dashboard/" 
                   style="display: inline-block; padding: 12px 30px; background: linear-gradient(90deg, #0d6efd, #6a11cb); color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View Dashboard
                </a>
            </p>
            
            <p style="color: #666; font-size: 12px; text-align: center; margin-top: 30px;">
                This is an automated message from Rate.me Feedback System
            </p>
        </div>
    </body>
    </html>
    """
    plain_message = strip_tags(html_message)
    
    try: 
        msg = EmailMultiAlternatives(
            
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [lecturer.email]
            
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
def send_suggestion_generated_notification(lecturer, suggestion):
    """Send email when the AI suggestions are generated"""
    subject = "New AI suggestions are ready for you to check out!"
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <h2 style="color: white; text-align: center;">💡 New AI Suggestions Ready!</h2>
        </div>
        
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background: #f8f9fa;">
            <h3 style="color: #28a745;">Hi {lecturer.get_full_name()},</h3>
            
            <p>Your AI-powered improvement suggestions have been generated based on <strong>{suggestion.based_on_feedback_count} feedback items</strong>.</p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <p style="white-space: pre-line; font-size: 14px;">{suggestion.suggestions_text[:500]}...</p>
            </div>
            
            <p style="text-align: center;">
                <a href="http://localhost:8000/dashboard/" 
                   style="display: inline-block; padding: 12px 30px; background: linear-gradient(90deg, #28a745, #20c997); color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View Full Suggestions
                </a>
            </p>
            
            <p style="color: #666; font-size: 12px; text-align: center; margin-top: 30px;">
                Rate.me - Powered by AI
            </p>
        </div>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        msg = EmailMultiAlternatives(
            
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [lecturer.email]
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error dending email: {e}")
        return False
        