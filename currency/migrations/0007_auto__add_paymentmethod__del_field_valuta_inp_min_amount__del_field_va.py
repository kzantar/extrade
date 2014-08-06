# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PaymentMethod'
        db.create_table(u'currency_paymentmethod', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('method', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('commission', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
            ('min_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8)),
            ('max_amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8)),
            ('valuta', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payment_method', to=orm['currency.Valuta'])),
            ('bank', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'currency', ['PaymentMethod'])

        # Deleting field 'Valuta.inp_min_amount'
        db.delete_column(u'currency_valuta', 'inp_min_amount')

        # Deleting field 'Valuta.commission_out'
        db.delete_column(u'currency_valuta', 'commission_out')

        # Deleting field 'Valuta.out_min_amount'
        db.delete_column(u'currency_valuta', 'out_min_amount')

        # Deleting field 'Valuta.out_max_amount'
        db.delete_column(u'currency_valuta', 'out_max_amount')

        # Deleting field 'Valuta.commission_inp'
        db.delete_column(u'currency_valuta', 'commission_inp')

        # Deleting field 'Valuta.bank'
        db.delete_column(u'currency_valuta', 'bank')

        # Deleting field 'Valuta.inp_max_amount'
        db.delete_column(u'currency_valuta', 'inp_max_amount')


    def backwards(self, orm):
        # Deleting model 'PaymentMethod'
        db.delete_table(u'currency_paymentmethod')

        # Adding field 'Valuta.inp_min_amount'
        db.add_column(u'currency_valuta', 'inp_min_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.commission_out'
        db.add_column(u'currency_valuta', 'commission_out',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2),
                      keep_default=False)

        # Adding field 'Valuta.out_min_amount'
        db.add_column(u'currency_valuta', 'out_min_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=10, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.out_max_amount'
        db.add_column(u'currency_valuta', 'out_max_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8),
                      keep_default=False)

        # Adding field 'Valuta.commission_inp'
        db.add_column(u'currency_valuta', 'commission_inp',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2),
                      keep_default=False)

        # Adding field 'Valuta.bank'
        db.add_column(u'currency_valuta', 'bank',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Valuta.inp_max_amount'
        db.add_column(u'currency_valuta', 'inp_max_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=14, decimal_places=8),
                      keep_default=False)


    models = {
        u'currency.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'bank': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'min_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '14', 'decimal_places': '8'}),
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