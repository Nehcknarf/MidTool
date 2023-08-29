from pathlib import Path


# Config path
consumable_cabinet_cfg_path = "/nubomed/consumable-cabinet-service/conf/"
# drug_cabinet_cfg_path = "/nubomed/midpkg/drug-middleware/conf/"
drug_cabinet_cfg_path = "D:/Downloads/conf/"
ecart_cfg_path = "/nubomed/ecart-service/conf/"

# Config file
cfg_file_name = {
    "nvr": "application-nvr.yml",
    "extern": "application-extern.yml",
    "sync": "application-sync.yml",
    "ws": "application-ws.yml",
    "mcc": "application-mcc.yml",
    "action_delay": "application-action-delay.yml"
}

if Path(consumable_cabinet_cfg_path).exists():
    cfg_root_path = Path(consumable_cabinet_cfg_path)
    # 耗材
    product_type = 0
elif Path(drug_cabinet_cfg_path).exists():
    cfg_root_path = Path(drug_cabinet_cfg_path)
    # 药品
    product_type = 1
elif Path(ecart_cfg_path).exists():
    cfg_root_path = Path(ecart_cfg_path)
    # 抢救车
    product_type = 2
else:
    cfg_root_path = Path()
    product_type = -1

sync_cfg_path = cfg_root_path / cfg_file_name["sync"]
nvr_cfg_path = cfg_root_path / cfg_file_name["nvr"]
extern_cfg_path = cfg_root_path / cfg_file_name["extern"]
ws_cfg_path = cfg_root_path / cfg_file_name["ws"]
mcc_cfg_path = cfg_root_path / cfg_file_name["mcc"]
action_delay_cfg_path = cfg_root_path / cfg_file_name["action_delay"]
