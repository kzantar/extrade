# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Valuta'
        db.create_table(u'currency_valuta', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
        ))
        db.send_create_signal(u'currency', ['Valuta'])

        # Adding model 'TypePair'
        db.create_table(u'currency_typepair', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('left', self.gf('django.db.models.fields.related.ForeignKey')(related_name='left_right', to=orm['currency.Valuta'])),
            ('right', self.gf('django.db.models.fields.related.ForeignKey')(related_name='funds_right', to=orm['currency.Valuta'])),
            ('commission', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'currency', ['TypePair'])

        # Adding unique constraint on 'TypePair', fields ['left', 'right']
        db.create_unique(u'currency_typepair', ['left_id', 'right_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'TypePair', fields ['left', 'right']
        db.delete_unique(u'currency_typepair', ['left_id', 'right_id'])

        # Deleting model 'Valuta'
        db.delete_table(u'currency_valuta')

        # Deleting model 'TypePair'
        db.delete_table(u'currency_typepair')


    models = {
        u'currency.typepair': {
            'Meta': {'unique_together': "(('left', 'right'),)", 'object_name': 'TypePair'},
            'commission': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'left_right'", 'to': u"orm['currency.Valuta']"}),
            'right': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'funds_right'", 'to': u"orm['currency.Valuta']"})
        },
        u'currency.valuta': {
            'Meta': {'object_name': 'Valuta'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['currency']