from django.db import models
from django.contrib.auth.models import User

class FinancialRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='records', null=True, blank=True)

    CATEGORY_CHOICES = [
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
        ('OTHER', 'Other'),
    ]

    date = models.DateField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount}"

    class Meta:
        ordering = ['-date']
