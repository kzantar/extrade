# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Valuta.out_min_amount'
        db.add_column(u'currency_valuta', 'out_min_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.out_max_amount'
        db.add_column(u'currency_valuta', 'out_max_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.inp_min_amount'
        db.add_column(u'currency_valuta', 'inp_min_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.inp_max_amount'
        db.add_column(u'currency_valuta', 'inp_max_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Valuta.out_min_amount'
        db.delete_column(u'currency_valuta', 'out_min_amount')

        # Deleting field 'Valuta.out_max_amount'
        db.delete_column(u'currency_valuta', 'out_max_amount')

        # Deleting field 'Valuta.inp_min_amount'
        db.delete_column(u'currency_valuta', 'inp_min_amount')

        # Deleting field 'Valuta.inp_max_amount'
        db.delete_column(u'currency_valuta', 'inp_max_amount')


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
            'inp_max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'inp_min_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '8'}),
            'out_max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'out_min_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '8'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['currency']