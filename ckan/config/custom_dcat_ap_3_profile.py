from .euro_dcat_ap_3 import EuropeanDCATAP3Profile 
from rdflib import URIRef, Literal
from rdflib.namespace import RDF, SKOS
from ckanext.dcat.profiles import DCATAP
import logging

log = logging.getLogger(__name__)


HVD_CATEGORIES = {
    "geospatial": {
        "uri": "http://data.europa.eu/bna/c_ac64a52d",
        "labels": [("en", "Geospatial"), ("ga", "Geospásúil")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "earth_observation": {
        "uri": "http://data.europa.eu/bna/c_earthobs",
        "labels": [("en", "Earth Observation"), ("ga", "Breathnóireacht Domhanda")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "environment": {
        "uri": "http://data.europa.eu/bna/c_environment",
        "labels": [("en", "Environment"), ("ga", "Comhshaol")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "meteorological": {
        "uri": "http://data.europa.eu/bna/c_meteorological",
        "labels": [("en", "Meteorological"), ("ga", "Meitéareolaíoch")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "statistics": {
        "uri": "http://data.europa.eu/bna/c_statistics",
        "labels": [("en", "Statistics"), ("ga", "Staidreamh")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "companies": {
        "uri": "http://data.europa.eu/bna/c_companies",
        "labels": [("en", "Companies and Corporate Ownership"), ("ga", "Cuideachtaí agus Úinéireacht Chorparáideach")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    },
    "mobility": {
        "uri": "http://data.europa.eu/bna/c_mobility",
        "labels": [("en", "Mobility"), ("ga", "Soghluaisteacht")],
        "scheme": "http://data.europa.eu/bna/asd487ae75"
    }
}


class CustomDcatApProfile(EuropeanDCATAP3Profile):
    def profile(self):
        log.info(">>> METODO profile() CHIAMATO <<<")
        return 'custom_dcat_ap_3_profile'

    def __init__(self, *args, **kwargs):
        super(CustomDcatApProfile, self).__init__(*args, **kwargs)
        log.info(">>> PROFILO PERSONALIZZATO INIZIALIZZATO <<<")

    def _graph_from_dataset_v3(self, dataset_dict, dataset_ref):
        super(CustomDcatApProfile, self)._graph_from_dataset_v3(dataset_dict, dataset_ref)
        log.info(">>> PROFILO PERSONALIZZATO ATTIVATO <<<")


        # Cerca anche tra gli extras
        hvd_category = dataset_dict.get('hvd_category')
        if not hvd_category:
            extras = {extra['key']: extra['value'] for extra in dataset_dict.get('extras', [])}
            hvd_category = extras.get('hvd_category')

        if hvd_category in HVD_CATEGORIES:
            cat = HVD_CATEGORIES[hvd_category]
            concept_uri = URIRef(cat["uri"])

            # Rimuove eventuali valori letterali associati a dcatap:hvdCategory
            for _, _, obj in self.g.triples((dataset_ref, DCATAP.hvdCategory, None)):
                if isinstance(obj, Literal):
                    self.g.remove((dataset_ref, DCATAP.hvdCategory, obj))
                    
            self.g.add((dataset_ref, DCATAP.hvdCategory, concept_uri))
            self.g.add((concept_uri, RDF.type, SKOS.Concept))
            self.g.add((concept_uri, SKOS.inScheme, URIRef(cat["scheme"])))
            for lang, label in cat["labels"]:
                self.g.add((concept_uri, SKOS.prefLabel, Literal(label, lang=lang)))
