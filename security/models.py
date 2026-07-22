from django.db import models


class CTFFlag(models.Model):
    """Stores CTF flags that can be exfiltrated via SQLi challenges."""
    challenge_id = models.CharField(max_length=50, unique=True)
    flag = models.CharField(max_length=200)
    category = models.CharField(max_length=50, default='SQLi')
    difficulty = models.CharField(max_length=20, default='Intermediate')

    class Meta:
        verbose_name = 'CTF Flag'
        verbose_name_plural = 'CTF Flags'

    def __str__(self):
        return f'{self.challenge_id} → {self.flag}'
