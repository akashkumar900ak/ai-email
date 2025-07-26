class ReplyGenerator:
    def generate_reply(self, email_body, classification="general"):
        email_body = email_body.lower()

        if classification == "personal":
            if "coffee" in email_body:
                return "Sounds great! I'm up for coffee this weekend. When and where?"
            elif "dinner" in email_body:
                return "Dinner sounds lovely! Let’s pick a time."
            elif "movie" in email_body:
                return "That sounds like fun! Let me know the time and movie."
            else:
                return "Hey! Great to hear from you. Let me know more."

        elif classification == "work":
            if "deadline" in email_body or "project" in email_body:
                return "Thanks for the update. I’ll make sure everything is on track and share progress shortly."
            elif "meeting" in email_body:
                return "Thanks for scheduling the meeting. I'll be there."
            else:
                return "Thank you for your message. I’ll review it and get back to you soon."

        elif classification == "spam":
            return "No reply required."

        else:
            # fallback generic
            return "Thanks for reaching out. I'll get back to you soon."
