from pydantic import BaseModel, EmailStr


class NewsletterSignup(BaseModel):
    email: EmailStr
