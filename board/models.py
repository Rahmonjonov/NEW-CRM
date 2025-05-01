from django.db import models
from account.models import Account, Company
from datetime import datetime

SMS_template_choise = (
    ("Ro'yxatdan o'tish uchun", "Ro'yxatdan o'tish uchun"),
    ("Tug'ilgan kun", "Tug'ilgan kun"),
    ("Bayram va boshqalar", "Bayram va boshqalar"),
)


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    comment = models.TextField()

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class Payment_type(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class CategoryProduct(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=220)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Viloyat'


class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Tuman'


class LeadPoles(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.IntegerField(default=-1)

    def __str__(self): return self.company.name + ' ' + self.name


class Lead(models.Model):
    status_types = (
        (0, "Lead boardda"),
        (1, "status1"),
        (4, "Yo'qotish"),
        (5, "Muvaffaqqiyatli yakunlash"),
        (6, "Promouter"),
    )
    degr = (
        (1, "Past"),
        (2, "O`rta"),
        (3, "Yuqori"),
    )
    joinByChoise = (
        (0, "Odatiy"),
        (1, "Telegram orqali")
    )
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, null=True, blank=True)
    price = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    finishedPrice = models.IntegerField(default=0)
    company = models.CharField(max_length=255, null=True, blank=True)
    companyAddress = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=0, choices=status_types)
    pole = models.ForeignKey(LeadPoles, on_delete=models.CASCADE, null=True, blank=True, default=None)
    date = models.DateTimeField(auto_now_add=True)
    finishedDate = models.DateTimeField(null=True, blank=True)
    created_user = models.ForeignKey(Account, on_delete=models.CASCADE)
    degree = models.IntegerField(choices=degr, default=1)
    phone = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    abcxyz = models.CharField(max_length=255, null=True)
    step1 = models.TextField(default="-", blank=True, null=True)
    step2 = models.TextField(default="-", blank=True, null=True)
    step3 = models.TextField(default="-", blank=True, null=True)
    step4 = models.TextField(default="-", blank=True, null=True)
    step5 = models.TextField(default="-", blank=True, null=True)
    sms_send = models.BooleanField(default=False, blank=True)

    note = models.TextField(blank=True, null=True)
    debt = models.IntegerField(default=0)

    joinBy = models.IntegerField(default=0, choices=joinByChoise)
    tg_chatid = models.IntegerField(default=0)

    join_from = models.CharField(max_length=150, blank=True, null=True, default="")
    phone2 = models.CharField(max_length=100, blank=True, null=True, default="")
    tg_id = models.CharField(max_length=100, blank=True, null=True)

    validity_period = models.DateField(null=True, blank=True)
    referral = models.ForeignKey('Referral', on_delete=models.CASCADE, null=True, blank=True)


    @property
    def get_validity_period(self):
        if self.validity_period is None:
            return True 
        today = datetime.now().date() 
        vald = self.validity_period
        if today >= vald: 
            return False
        else:
            return True

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        name = self.name
        if self.surname != None:
            name += self.surname
        return name


class LeadAction(models.Model):
    status_types = (
        (0, "Lead yaratildi"),
        (1, "Lead taxrirlandi"),
        (2, "Status o'zgardi"),
        (3, "Izoh qo'shildi"),
        (4, "Pole o'zgardi"),
    )
    status_emotsiya = (
        (1, '🤔 Qarorsiz'),
        (2, '🤗 Qayta kelishuv'),
        (3, '😋 Info ehtiyoj'),
        (4, '🤓 Tasir etish kerak'),
        (5, '👏🏻 Tezkor sotish kerak'),
        (6, '🤩 Istemolchi'),
        (7, '✍🏻 Qo’shimcha kelishuv'),
        (8, '🙃 Etirozli'),
        (9, '😖 Shikoyatli'),
    )
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    status = models.IntegerField(default=0, choices=status_types)
    oldStatus = models.IntegerField(default=0)
    newStatus = models.IntegerField(default=0)
    oldpole = models.ForeignKey(LeadPoles, on_delete=models.SET_NULL, null=True, blank=True, related_name="old")
    newpole = models.ForeignKey(LeadPoles, on_delete=models.SET_NULL, null=True, blank=True, related_name="new")
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
    color = models.CharField(default="primary", max_length=255)
    emotsiya = models.IntegerField(choices=status_emotsiya, default=0)
    changer = models.ForeignKey(Account, on_delete=models.CASCADE)


class Shopping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    amount = models.BigIntegerField(default=0)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(Payment_type, on_delete=models.CASCADE)
    comment = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.lead.name + ' - ' + self.product.name


class Task(models.Model):
    status_types = (
        (0, "Ro'yxatga olindi"),
        (1, "Bajarilmoqda"),
        (2, "Bajarildi"),
        (3, "O'chirildi"),
    )
    lead_types = (
        (0, "Yangi"),
        (1, "Aloqa"),
        (2, "Uchrashuv"),
        (3, "Boshqa"),
    )
    name = models.CharField(max_length=255)
    note = models.TextField()
    status = models.IntegerField(default=0, choices=status_types)
    lead_status = models.IntegerField(default=0, choices=lead_types)
    date = models.DateTimeField(auto_now_add=True)
    finishedDate = models.DateTimeField(null=True)
    created_user = models.ForeignKey(Account, on_delete=models.CASCADE)
    customer = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name="task_customer")
    lead_action = models.ForeignKey(LeadAction, on_delete=models.CASCADE, null=True, blank=True)
    lead_date_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Telegram_user(models.Model):
    step_choise = (
        (0, 'Start'),
        (1, 'Contact'),
        (2, 'Name'),
        (3, 'Company'),
        (4, 'Company Address'),
        (5, 'Finished')
    )
    chat_id = models.IntegerField(default=0)
    name = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    companyAddress = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True)
    step = models.IntegerField(default=1, choices=step_choise)
    token = models.CharField(max_length=255, null=True, blank=True)


class SMSTemplate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(default="Ro'yxatdan o'tish uchun", choices=SMS_template_choise, max_length=100)
    date = models.DateField(blank=True, null=True)
    text = models.TextField(default="")
    leads = models.ManyToManyField(Lead, blank=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.company.name + " " + self.name


class SMSHistory(models.Model):
    smstemplate = models.ForeignKey(SMSTemplate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(blank=True, null=True)
    is_success = models.BooleanField(default=False)
    send_count = models.IntegerField(default=0)
    not_send_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.smstemplate.company.name} - {self.smstemplate.name}"


class AbstractRedirect_base(models.Model):
    # own_url = "http://127.0.0.1:8000/"
    own_url = "http://crm.backoffice.uz/"
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)

    telegram_url = models.URLField(max_length=400, blank=True, null=True, editable=False)
    instagram_url = models.URLField(max_length=400, blank=True, null=True, editable=False)
    facebook_url = models.URLField(max_length=400, blank=True, null=True, editable=False)
    youtube_url = models.URLField(max_length=400, blank=True, null=True, editable=False)
    tiktok_url = models.URLField(max_length=400, blank=True, null=True, editable=False)

    telegram_count = models.BigIntegerField(default=0, editable=False)
    instagram_count = models.BigIntegerField(default=0, editable=False)
    facebook_count = models.BigIntegerField(default=0, editable=False)
    youtube_count = models.BigIntegerField(default=0, editable=False)
    tiktok_count = models.BigIntegerField(default=0, editable=False)

    total_count = models.BigIntegerField(default=0, editable=False)

    class Meta:
        abstract = True


class UrlRedirect(AbstractRedirect_base):
    next_url = models.URLField(max_length=200)

    def generate_url(self):
        url = self.own_url + f"redirects/social/?pk={self.id}&next_url={self.next_url}"
        self.telegram_url = url + "&social=telegram"
        self.instagram_url = url + "&social=instagram"
        self.facebook_url = url + "&social=facebook"
        self.youtube_url = url + "&social=youtube"
        self.tiktok_url = url + "&social=tiktok"

    def save(self, *args, **kwargs):
        super(UrlRedirect, self).save(*args, **kwargs)
        self.generate_url()
        super(UrlRedirect, self).save(*args, **kwargs)


class NoteForm(AbstractRedirect_base):
    image = models.ImageField(upload_to='formImages/')

    def generate_url(self):
        url = self.own_url + f"redirects/form/?pk={self.id}"
        self.telegram_url = url + "&social=telegram"
        self.instagram_url = url + "&social=instagram"
        self.facebook_url = url + "&social=facebook"
        self.youtube_url = url + "&social=youtube"
        self.tiktok_url = url + "&social=tiktok"

    def save(self, *args, **kwargs):
        super(NoteForm, self).save(*args, **kwargs)
        self.generate_url()
        super(NoteForm, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class FormQuestion(models.Model):
    form = models.ForeignKey(NoteForm, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FormAnswer(models.Model):
    social_choise = (
        ("telegram", "telegram"),
        ("instagram", "instagram"),
        ("facebook", "facebook"),
        ("youtube", "youtube"),
        ("tiktok", "tiktok")
    )
    form = models.ForeignKey(NoteForm, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    join_by = models.CharField(max_length=20, choices=social_choise, default="telegram")

    def __str__(self):
        return self.form.name + " answer"


class AnswerQuestion(models.Model):
    question = models.ForeignKey(FormQuestion, on_delete=models.SET_NULL, null=True)
    answer = models.ForeignKey(FormAnswer, on_delete=models.SET_NULL, null=True)
    text = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.text

from urllib.parse import urlparse, parse_qs


class Instruktsya(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to="board_instruktsya/", blank=True, null=True)
    photo = models.FileField(upload_to="board_instruktsya_photo/", blank=True, null=True)
    video_link = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime.now())
    
    @property
    def youtube_id(self):
        parsed_url = urlparse(self.video_link)
        if parsed_url.hostname == "youtu.be":
            return parsed_url.path[1:]
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            query = parse_qs(parsed_url.query)
            return query.get("v", [None])[0]
        return None

    @property
    def embed_url(self):
        video_id = self.youtube_id
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return ""


class Referral(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_activate = models.BooleanField(default=True)