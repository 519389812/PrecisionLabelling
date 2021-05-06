import re


check_all = True  # 检查包含未接收的旅客


def details_divide(text):
    l1 = text.find("CTC-")
    l2 = text.find("PSPT-")
    l = l1 if l1 != -1 else l2
    name_pattern = re.compile(r"\s\d\.\s[A-Za-z]+/?([A-Za-z]+)?")
    pnr_pattern = re.compile(r"\sPNR\sRL\s{2}\w{6}\s")
    bn_pattern = re.compile(r"\s?BN\d{3}\s")
    seat_pattern = re.compile(r"\s\*?\d{1,2}[A-Za-z]\s")
    seat_class_pattern = re.compile(r"\s[A-Za-z]{1}\s")
    destination_pattern = re.compile(r"\s[A-Za-z]{1}\s[A-Za-z]{3}\s")
    group_pattern = re.compile(r'\s\d\.\s[A-Za-z]+/?([A-Za-z]+)?\s*[A-Za-z]{1,2}\d{1,2}\s')
    bag_pattern = re.compile(r"\sBAG\d/\d{1,3}/\d\s")
    fba_pattern = re.compile(r"\sFBA/\d{1,2}[A-Za-z]{1,2}\s")
    gfba_pattern = re.compile(r"\sGFBA/[A-Za-z0-9]+")
    gfba_text_pattern = re.compile(r"\s(?:GFB\s|null)[A-Za-z]{3}\d{4,6}\sAGT\d{4,5}/\d{2}[A-Za-z]{3}\d{4}/(?:GFBA|null)/[A-Za-z0-9]{4,5}")  # GFB CAN16537 AGT3420/22MAY0503/GFBA/H9W04 | nullCAN16537 AGT3420/22MAY0503/null/BN65
    ff_pattern = re.compile(r"\sFF/[A-Za-z]{2}\s[A-Za-z0-9]+/[A-Za-z]?/?\S{1,2}?\s")
    ures_pattern = re.compile(r"\sURES\s")
    upg_pattern = re.compile(r"\sUPG[A-Za-z]\s")
    tkt_pattern = re.compile(r"\sET\sTKNE/\d{13}/\d\s")
    inf_pattern = re.compile(r"\sINF\d/\d\s")
    inf_name_pattern = re.compile(r"\sINF-.*")
    inf_tkt_pattern = re.compile(r"\sET\sTKNE/INF\d{13}/\d\s")
    psm_pattern = re.compile(r"\sPSM-[\S\s]*\s(?:PSPT-|CTC-|\s{5})?")
    expc_pattern = re.compile(r"\sEXPC-\s\d{1,2}/\d{1,3}[A-Za-z]{2}-\d{2,3}LCM.*")
    exbg_pattern = re.compile(r"\sEXBG-\d{1,3}KG/.*")
    asvc_pattern = re.compile(r"\sASVC-\s[A-Za-z]/[A-Za-z0-9]{3}/[A-Za-z]{4}/.*")
    pspt_pattern = re.compile(r"\sPSPT-.*/.*/.*")
    paxlst_pattern = re.compile(r"\sPAXLST\s+:\w+/\w+.*")
    paxinfo_pattern = re.compile(r"\sPAX\sINFO\s:.*")
    passport_pattern = re.compile(r"\sPASSPORT\s:.*")
    inf_paxlst_pattern = re.compile(r'\sPSPT-.*/INF')
    foid_pattern = re.compile(r'\sFOID/\S*\s')
    cnin_pattern = re.compile(r'\sCNIN/.*\s')
    ckin_pattern = re.compile(r"\sCKIN\sOVR.*")
    acc_pattern = re.compile(r"\sACC\s[A-Za-z]{3}\d{4,6}\s(?:AGT\d{4,5}|EDI\W[A-Za-z]{2})/\d{2}[A-Za-z]{3}\d{4}.*")
    bc_pattern = re.compile(r"\sBC\s+[A-Za-z]{3}\d{4,6}\sAGT\d{4,5}/\d{2}[A-Za-z]{3}\d{4}.*")
    bagtag_pattern = re.compile(r'\sBAGTAG/((.*)?.{4}\d{6}/[A-Za-z]{3,4}.*\n)+')
    bgt_pattern = re.compile(r"BAG\s[A-Za-z]{3}\d{4,6}\sAGT\d{4,5}/\d{2}[A-Za-z]{3}\d{4}/\d{3}.*")
    security_pattern = re.compile(r"\s(?:SEC\s|null)[A-Za-z]{3}\d{4,6}\sAGT\d{4,5}/\d{2}[A-Za-z]{3}\d{4}/(?:.{2}-A|null)")
    inbound_pattern = re.compile(r"\sI/(?:[A-Za-z]{2}|[A-Za-z]\d|\d[A-Za-z])\d{3,4}/\d{2}[A-Za-z]{3}.*")
    outbound_pattern = re.compile(r"\sO/(?:[A-Za-z]{2}|[A-Za-z]\d|\d[A-Za-z])\d{3,4}/\d{2}[A-Za-z]{3}.*")
    gov_pattern = re.compile(r"\sGOV/[A-Za-z]{3}/[A-Za-z]{3}\s")
    esta_pattern = re.compile(r"\sESTA/[A-Za-z]/[A-Za-z]{3}\s")
    aqq_pattern = re.compile(r"\sAQQ/[A-Za-z]{3}/[A-Za-z]{3}\s")
    app_pattern = re.compile(r"\sAPP-.*")
    appi_pattern = re.compile(r"\sAPPI-.*")
    sec_pattern = re.compile(r"\sSEC\sTXT-.*")
    addff_pattern = re.compile(r"\sMOD\s[A-Za-z]{3}\d{4,6}\sAGT\d{4,5}/\d{2}[A-Za-z]{3}\d{4}/FF")
    exst_pattern = re.compile(r"\sEXST\s")
    pax_name = name_pattern.search(text[:l])
    pnr = pnr_pattern.search(text[:l])
    bn = bn_pattern.search(text[:l])
    seat = seat_pattern.search(text[:l])
    seat_class = seat_class_pattern.search(text[:l])
    destination = destination_pattern.search(text[:l])
    group_ = group_pattern.search(text[:l])
    bag = bag_pattern.search(text[:l])
    fba = fba_pattern.search(text[:l])
    gfba = gfba_pattern.search(text[:l])
    gfba_text = gfba_text_pattern.search(text)
    ff = ff_pattern.search(text[:l])
    ures = ures_pattern.search(text[:l])
    upg = upg_pattern.search(text[:l])
    tkt = tkt_pattern.search(text[:l])
    inf = inf_pattern.search(text[:l])
    inf_name = inf_name_pattern.search(text[:l])
    inf_tkt = inf_tkt_pattern.search(text[:l])
    psm = psm_pattern.search(text)
    expc = expc_pattern.search(text)
    exbg = exbg_pattern.search(text)
    asvc = asvc_pattern.findall(text)
    pspt = pspt_pattern.search(text)
    paxlst = paxlst_pattern.search(text)
    paxinfo = paxinfo_pattern.search(text)
    passport = passport_pattern.search(text)
    inf_paxlst = inf_paxlst_pattern.search(text)
    foid = foid_pattern.search(text[:l])
    cnin = cnin_pattern.search(text[:l])
    ckin = ckin_pattern.search(text)
    acc = acc_pattern.findall(text)
    bc = bc_pattern.findall(text)
    bagtag = bagtag_pattern.search(text)
    bgt = bgt_pattern.findall(text)
    security = security_pattern.findall(text)
    inbound = inbound_pattern.findall(text)
    outbound = outbound_pattern.findall(text)
    gov = gov_pattern.findall(text[:l])
    esta = esta_pattern.findall(text[:l])
    aqq = aqq_pattern.findall(text[:l])
    app = app_pattern.search(text)
    appi = appi_pattern.search(text)
    sec = sec_pattern.findall(text)
    addff = addff_pattern.search(text)
    exst = exst_pattern.search(text[:l])
    return pax_name, pnr, bn, seat, seat_class, destination, group_, bag, ff, fba, gfba, gfba_text, ures, upg, tkt,\
           inf, inf_name, inf_tkt, psm, expc, exbg, asvc, pspt, paxlst, paxinfo, passport, inf_paxlst, foid, cnin,\
           ckin, acc, bc, bagtag, bgt, security, inbound, outbound, gov, esta, aqq, app, appi, sec, addff, exst


def details_extract(text, flt_num='', flt_date='', is_accept=False):
    pax_name, pnr, bn, seat, seat_class, destination, group_, bag, ff, fba, gfba, gfba_text, ures, upg, tkt, inf,\
    inf_name, inf_tkt, psm, expc, exbg, asvc, pspt, paxlst, paxinfo, passport, inf_paxlst, foid, cnin, ckin, acc,\
    bc, bagtag, bgt, security, inbound, outbound, gov, esta, aqq, app, appi, sec, addff, exst = details_divide(text)
    if pax_name is None:
        return None
    name = pax_name.group().strip().split(' ')[1].split('/')
    last_name = name[0]
    try:
        first_name = name[1]
    except:
        first_name = ''
    pnr = pnr.group().strip()[-6:] if pnr is not None else ''
    bn = bn.group().strip() if bn is not None else ''
    if is_accept is True:
        if "XXX" in last_name or bn == "":
            return None
    else:
        if "XXX" in last_name:
            return None
    seat = seat.group().strip() if seat is not None else ''
    seat_class = seat_class.group().strip() if seat_class is not None else ''
    destination = destination.group().strip().split(" ")[-1] if destination is not None else ''
    group_ = group_.group().strip() if group_ is not None else ''
    group_ = re.search(r'\s?[A-Za-z]{1,2}\d{1,2}', group_).group().strip() if group_ != '' else ''
    bag = bag.group().strip().lstrip('BAG').split('/') if bag is not None else ''
    bag_pc = int(bag[0]) if bag != '' else 0
    bag_wt = int(bag[1]) if bag != '' else 0
    ff = ff.group().strip().split('/') if ff is not None else ''
    if ff != '':
        ff_airline, ff_number = ff[1].strip().split(' ')
        if len(ff) == 4:
            ff_level = ff[2]
        elif len(ff) == 3:
            ff_level = ff[-1]
        else:
            ff_level = ''
    else:
        ff_airline, ff_number, ff_level = '', '', ''
    fba = fba.group().strip().split('/')[1] if fba is not None else ''
    fba_num = int(re.search(r'\d{1,2}', fba).group()) if fba != '' else ''
    fba_unit = re.search(r'[A-Za-z]{1,2}', fba).group() if fba != '' else ''
    gfba = gfba.group().strip().split('/')[1] if gfba is not None else ''
    gfba_text = gfba_text.group().strip() if gfba_text is not None else ''
    ures = ures.group().strip() if ures is not None else ''
    upg = upg.group().strip() if upg is not None else ''
    tkt = tkt.group().strip().split('/')[1] if tkt is not None else ''
    inf = inf.group().strip().lstrip('INF').split('/')[0] if inf is not None else ''
    inf_name = inf_name.group().strip().split('-')[1] if inf_name is not None else ''
    inf_name = re.search(r"[A-Za-z]+/?[A-Za-z]+", inf_name) if inf_name != '' else ''
    if inf_name is None:
        inf_name = ''
    if inf_name != '':
        try:
            inf_last_name = inf_name.group().split('/')[0] if inf_name != '' else ''
            inf_first_name = inf_name.group().split('/')[1] if inf_name != '' else ''
        except:
            inf_last_name = inf_name.group()
            inf_first_name = ''
    else:
        inf_last_name = ''
        inf_first_name = ''
    inf_tkt = inf_tkt.group().strip().split('/')[1].lstrip('INF') if inf_tkt is not None else ''
    pspt_number = pspt.group().strip().split('-')[-1].split('/')[0] if pspt is not None else ''
    pspt_birthday = pspt.group().strip().split('-')[-1].split('/')[2] if pspt is not None else ''
    paxlst = paxlst.group().strip().split(':')[1].split('/') if paxlst is not None else ''
    pspt_last_name = paxlst[0] if paxlst != '' else ''
    pspt_first_name = paxlst[1] if paxlst != '' else ''
    # pspt_middle_name = paxlst[2] if paxlst != '' else ''
    paxinfo = paxinfo.group().strip().split(':')[1].split('/') if paxinfo is not None else ''
    resident = paxinfo[0] if paxinfo != '' else ''
    birthday = paxinfo[2] if paxinfo != '' else ''
    gender = paxinfo[6] if paxinfo != '' else ''
    passport = passport.group().strip().split(':')[1].split('/') if passport is not None else ''
    passport_number = passport[0] if passport != '' else ''
    passport_type = passport[1] if passport != '' else ''
    nationality = passport[3] if passport != '' else ''
    expiry = passport[5] if passport != '' else ''
    inf_paxlst = inf_paxlst.group().strip().split('-')[1].split('/') if inf_paxlst is not None else ''
    inf_passport = inf_paxlst[0] if inf_paxlst != '' else ''
    inf_nationality = inf_paxlst[1] if inf_paxlst != '' else ''
    inf_birthday = inf_paxlst[2] if inf_paxlst != '' else ''
    inf_gender = inf_paxlst[3] if inf_paxlst != '' else ''
    foid = foid.group().strip() if foid is not None else ''
    foid = foid[foid.find("NI")+2:] if foid.find("NI") != -1 else ''
    birthday = foid[6:14] if len(foid) == 18 else birthday
    cnin = cnin.group().strip().split("/")[-1] if cnin is not None else ''
    ckin = ckin.group().strip() if ckin is not None else ''
    acc = acc[-1].strip().split(' ') if len(acc) > 0 else ''
    acc_station = acc[1] if acc != '' else ''
    acc_agent = acc[2].split('/')[0] if acc != '' else ''
    acc_time = acc[2].split('/')[1] if acc != '' else ''
    bc = bc if len(bc) > 0 else ''
    if bc != '':
        bc_details = []
        for per_bc in bc:
            per_bc = per_bc.strip().replace('  ', ' ').split(' ')
            bc_station = per_bc[1]
            bc_agent = per_bc[2].split('/')[0]
            bc_time = per_bc[2].split('/')[1]
            bc_details.append(",".join([bc_station, bc_agent, bc_time]))
        bc = ";".join(bc_details)
    bagtag = bagtag.group().strip() if bagtag is not None else ''
    bagtag = re.findall(r'(?:\d{4}|\s[A-Za-z]{2}\s)\d{6}/[A-Za-z]{3,4}', bagtag) if bagtag != '' else ''
    bagtag = ",".join(bagtag)
    bgt = bgt if len(bgt) > 0 else ''
    if bgt != '':
        bgt_details = []
        for per_bag in bgt:
            per_bag = per_bag.strip().split(' ')
            bag_station = per_bag[1]
            bag_agent = per_bag[2].split('/')[0]
            bag_time = per_bag[2].split('/')[1]
            bgt_details.append(",".join([bag_station, bag_agent, bag_time]))
        bgt = ";".join(bgt_details)
    try:
        last_bgt_station = bag_station[:3] if bgt != '' else ''
        last_bgt_agent = bag_agent.lstrip('AGT') if bgt != '' else ''
    except:
        last_bgt_station, last_bgt_agent = '', ''
    security = security if len(security) > 0 else ''
    if security != '':
        security_details = []
        for per_security in security:
            per_security = per_security.strip().split(' ')
            security_time = per_security[-1].split('/')[1]
            security_details.append(",".join([security_time]))
        security = ";".join(security_details)
    inbound = inbound if len(inbound) > 0 else ''
    if inbound != '':
        inbound_details = []
        for per_inbound in inbound:
            per_inbound = per_inbound.strip()[:39].split(' ')
            per_inbound = [x for x in per_inbound if x != '']
            inbound_flt = per_inbound[0].split('/')[1]
            inbound_date = per_inbound[0].split('/')[2]
            inbound_apt = per_inbound[-1]
            if len(per_inbound) == 5:
                inbound_bn = per_inbound[1]
                inbound_seat = per_inbound[2]
            elif len(per_inbound) == 4:
                inbound_bn = ''
                inbound_seat = per_inbound[1]
            else:
                inbound_bn = ''
                inbound_seat = ''
            inbound_details.append(",".join([inbound_flt, inbound_date, inbound_bn, inbound_seat, inbound_apt]))
        inbound = ";".join(inbound_details)
    outbound = outbound if len(outbound) > 0 else ''
    if outbound != '':
        outbound_details = []
        for per_outbound in outbound:
            per_outbound = per_outbound.strip()[:39].split(' ')
            per_outbound = [x for x in per_outbound if x != '']
            outbound_flt = per_outbound[0].split('/')[1]
            outbound_date = per_outbound[0].split('/')[2]
            outbound_apt = per_outbound[-1]
            if len(per_outbound) == 5:
                outbound_bn = per_outbound[1]
                outbound_seat = per_outbound[2]
            elif len(per_outbound) == 4:
                outbound_bn = ''
                outbound_seat = per_outbound[1]
            else:
                outbound_bn = ''
                outbound_seat = ''
            outbound_details.append(",".join([outbound_flt, outbound_date, outbound_bn, outbound_seat, outbound_apt]))
        outbound = ";".join(outbound_details)
    gov = (",".join(gov)).strip() if len(gov) > 0 else ''
    esta = (",".join(esta)).strip() if len(esta) > 0 else ''
    aqq = (",".join(aqq)).strip() if len(aqq) > 0 else ''
    app = app.group().strip() if app is not None else ''
    appi = appi.group().strip() if appi is not None else ''
    sec = (",".join(sec)).strip() if len(sec) > 0 else ''
    if psm is not None:
        psm_loc = psm.group().strip().find("CTC-")
        psm_loc = psm.group().strip().find("PSPT-") if psm_loc == -1 else psm_loc
        psm = psm.group().strip()[:psm_loc].replace(" ", "")
        psm = psm.replace("\r\n", "")
    else:
        psm = ''
    expc = expc.group().strip() if expc is not None else ''
    exbg = exbg.group().strip() if exbg is not None else ''
    asvc = asvc if len(asvc) > 0 else ''
    if asvc != '':
        asvc = ";".join([per_asvc.strip() for per_asvc in asvc])
    addff = addff.group().strip() if addff is not None else ''
    exst = exst.group().strip() if exst is not None else ''
    unstructured_data = {
        'last_name': last_name, 'first_name': first_name, 'pnr': pnr, 'bn': bn, 'seat': seat, 'seat_class': seat_class,
        'destination': destination, 'group_': group_, 'bag_pc': bag_pc, 'bag_wt': bag_wt, 'ff_airline': ff_airline,
        'ff_number': ff_number, 'ff_level': ff_level, 'fba_num': fba_num, 'fba_unit': fba_unit, 'gfba': gfba,
        'gfba_text': gfba_text, 'ures': ures, 'upg': upg, 'tkt': tkt, 'inf': inf, 'inf_last_name': inf_last_name,
        'inf_first_name': inf_first_name, 'inf_tkt': inf_tkt, 'pspt_number': pspt_number,
        'pspt_birthday': pspt_birthday, 'pspt_last_name': pspt_last_name, 'pspt_first_name': pspt_first_name,
        'resident': resident, 'birthday': birthday, 'gender': gender, 'passport_number': passport_number,
        'passport_type': passport_type, 'nationality': nationality, 'expiry': expiry, 'inf_passport': inf_passport,
        'inf_nationality': inf_nationality, 'inf_birthday': inf_birthday, 'inf_gender': inf_gender, 'foid': foid,
        'cnin': cnin, 'ckin': ckin, 'acc_station': acc_station, 'acc_agent': acc_agent, 'acc_time': acc_time, 'bc': bc,
        'bagtag': bagtag, 'bgt': bgt, 'last_bgt_station': last_bgt_station, 'last_bgt_agent': last_bgt_agent,
        'security': security, 'inbound': inbound, 'outbound': outbound, 'gov': gov, 'esta': esta, 'aqq': aqq,
        'app': app, 'appi': appi, 'sec': sec, 'psm': psm, 'expc': expc, 'exbg': exbg, 'asvc': asvc, 'addff': addff,
        'exst': exst, 'flt_num': flt_num, 'flt_date': flt_date,
    }
    return unstructured_data


if __name__ == "__main__":
    pass
