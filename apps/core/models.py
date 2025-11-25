# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Modelos MedicationBatch e BatchLocation foram removidos
# A funcionalidade de lotes foi completamente removida do sistema
