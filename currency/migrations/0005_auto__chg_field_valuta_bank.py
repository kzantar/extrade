# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Valuta.bank'
        db.alter_column(u'currency_valuta', 'bank', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Valuta.bank'
        db.alter_column(u'currency_valuta', 'bank', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
        u'currency.typepair': {
            'Meta': {'unique_together': "(('left', 'right'),)", 'object_name': 'TypePair'},
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_right'", 'to': u"orm['currency.Valuta']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funds_right'", 'to': u"orm['currency.Valuta']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'currency.valuta': {
            'Meta': {'object_name': 'Valuta'},
            'bank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'commission_inp': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'commission_out': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['currency']