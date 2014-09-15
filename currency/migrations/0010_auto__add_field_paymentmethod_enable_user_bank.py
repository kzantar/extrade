# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PaymentMethod.enable_user_bank'
        db.add_column(u'currency_paymentmethod', 'enable_user_bank',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PaymentMethod.enable_user_bank'
        db.delete_column(u'currency_paymentmethod', 'enable_user_bank')


    models = {
        u'currency.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'disable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enable_user_bank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'max_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'min_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'min_commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'valuta': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_method'", 'to': u"orm['currency.Valuta']"})
        },
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['currency']