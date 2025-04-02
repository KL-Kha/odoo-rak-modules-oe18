import requests
import logging
import re

from odoo import api, models


class MesRecord(models.AbstractModel):
    _name = "rak.mes.record"

    def mes_record_automated_on_create(self, records):
        pattern = 'Trackpac'
        for rec in records:
            logging.info(f"In if condition.........{rec.x_studio_product_name}")
            if rec.x_studio_success is True and rec.x_studio_product_name and \
                    re.search(pattern, rec.x_studio_product_name,
                              re.IGNORECASE):
                print("In if condition.........")
                payload = [{
                    "dev_eui": rec.x_deveui,
                    "app_eui": rec.x_appeui,
                    "app_key": rec.x_appkey,
                    "claim_code": rec.x_serial,
                    "region": rec.x_frequency,
                    "device_type": 7,
                    "device_brand_id": 11,
                    "hosted": "hosted"
                }]
                url = "https://v2-api.trackpac.io/device/insert/8dff078a-b66f-42fd-83ee-815ae9563820"
                res = requests.post(url, json=payload)
                data = res.json()
                logging.info(
                    f"Trackpac Response {res.status_code} {rec.id} \
                {rec.x_studio_production_order_id.product_id.name}")

                if res.status_code == 200:
                    devices_added = data.get('devices_added') and data.get('devices_added').get('devices')
                    devices_failed = data.get('devices_failed') and data.get('devices_failed').get('devices')
                    logging.info(
                        f"Trackpac Response {devices_failed} {devices_added} ")

                    if devices_added:

                        written = rec.write({
                            "x_wisdm_pushed": True,
                            "x_wisdm_pushed_count": len(devices_added),
                            "x_wisdm_reponse": data
                        })
                        logging.info(
                            f"Trackpac Response  {written}")
                    elif devices_failed:

                        written = rec.write({
                            "x_wisdm_failed": True,
                            "x_wisdm_failed_count": rec.x_wisdm_failed_count + 1,
                            "x_wisdm_reponse": data
                        })
                else:
                    rec.x_wisdm_reponse = data

    def mes_record_cron(self):
        pattern = 'trackpac'
        mes_recs = self.env['x_rak_mes_record'].sudo().search([('x_studio_success', '=', True),
                                                               '|', ('x_wisdm_failed_count', '<=', 3),
                                                               ('x_wisdm_failed_count', '=', False),
                                                               ('x_wisdm_pushed', '!=', True)
                                                               ])
        logging.info(f"Trackpack Scheduler before filter...{len(mes_recs)}")
        mes_recs = mes_recs.filtered(lambda rec: rec.x_studio_production_order_id.product_id.name and
                                                 pattern in rec.x_studio_product_name)

        logging.info(f"Trackpack Scheduler Starting...{len(mes_recs)}")
        for rec in mes_recs[:100]:

            payload = [{
                "dev_eui": rec.x_deveui,
                "app_eui": rec.x_appeui,
                "app_key": rec.x_appkey,
                "claim_code": rec.x_serial,
                "region": rec.x_frequency,
                "device_type": 7,
                "device_brand_id": 11,
                "hosted": "hosted"
            }]
            url = "https://v2-api.trackpac.io/device/insert/8dff078a-b66f-42fd-83ee-815ae9563820"
            res = requests.post(url, json=payload)
            data = res.json()
            logging.info(
                f"Trackpac Response {res.status_code} {rec.id} {rec.x_studio_production_order_id.product_id.name}")
            if res.status_code == 200:
                devices_added = data.get('devices_added') and data.get('devices_added').get('devices')
                devices_failed = data.get('devices_failed') and data.get('devices_failed').get('devices')
                logging.info(
                    f"Trackpac Response {devices_failed} {devices_added} ")
                if devices_added:
                    written = rec.write({
                        "x_wisdm_pushed": True,
                        "x_wisdm_pushed_count": len(devices_added),
                        "x_wisdm_reponse": data
                    })
                    logging.info(
                        f"Trackpac Response  {written} ")
                elif devices_failed:
                    written = rec.write({
                        "x_wisdm_failed": True,
                        "x_wisdm_failed_count": rec.x_wisdm_failed_count + 1,
                        "x_wisdm_reponse": data
                    })
                self._cr.commit()

            else:
                rec.x_wisdm_reponse = data
