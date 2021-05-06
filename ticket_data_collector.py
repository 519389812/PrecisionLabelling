import re


def details_divide(text):
    issued_pattern = re.compile(r'ISSUED\sBY:.*?\s\s')
    org_dst_pattern = re.compile(r'ORG/DST:\s[A-Za-z]{3}/[A-Za-z]{3}')
    e_r_pattern = re.compile(r'E/R:.*')
    tour_code_pattern = re.compile(r'TOUR\sCODE:.*')
    passenger_name_pattern = re.compile(r'PASSENGER:.*')
    exch_pattern = re.compile(r'EXCH:.*?\s\s')
    conj_pattern = re.compile(r'\s?CONJ\sTKT:.*')
    from_pattern = re.compile(r'[A-Za-z]?\s?FM:[0-9]?\s?[A-Za-z]{3}.*\n?\r?\s+\n?\r?.*')
    to_pattern = re.compile(r'[A-Za-z]?\s?TO:[0-9]?\s?[A-Za-z]{3}.*\n?\r?.*\n?\r?.*\n?\r?.*\n?\r?.*TO:')
    fare_pattern = re.compile(r'FARE:.*\|')
    tax_pattern = re.compile(r'TAX:.*\|')
    total_pattern = re.compile(r'TOTAL:.*\|')
    issued = issued_pattern.search(text)
    org_dst = org_dst_pattern.search(text)
    e_r = e_r_pattern.search(text)
    tour_code = tour_code_pattern.search(text)
    passenger_name = passenger_name_pattern.search(text)
    exch = exch_pattern.search(text)
    conj = conj_pattern.search(text)
    from_ = from_pattern.search(text)
    to_ = to_pattern.findall(text)
    fare = fare_pattern.search(text)
    tax = tax_pattern.findall(text)
    total = total_pattern.search(text)
    date = text[:text.find('_')]
    return issued, org_dst, e_r, tour_code, passenger_name, exch, conj, from_, to_, fare, tax, total, date


def details_extract(text):
    issued, org_dst, e_r, tour_code, passenger_name, exch, conj, from_, to_, fare, tax, total, date = details_divide(text)
    passenger_name = passenger_name.group().split(':')[-1].strip() if passenger_name is not None else ''
    if passenger_name == '':
        return None
    issued = issued.group().split(':')[-1].strip() if issued is not None else ''
    org_dst = org_dst.group().split(':')[-1].strip() if org_dst is not None else ''
    if '/' in org_dst:
        org, dst = org_dst.split('/')
    else:
        org, dst = '', ''
    e_r = e_r.group().split(':')[-1].strip() if e_r is not None else ''
    tour_code = tour_code.group().split(':')[-1].strip() if tour_code is not None else ''
    if '/' in passenger_name:
        last_name, first_name = passenger_name.split('/')
    else:
        last_name, first_name = passenger_name, ''
    exch = exch.group().split(':')[-1].strip() if exch is not None else ''
    conj = conj.group().split(':')[-1].strip() if conj is not None else ''
    from_to_pattern = re.compile(r'[A-Za-z]{3}\s[A-Za-z0-9]{2}\s[A-Za-z0-9]{3,4}\s[A-Za-z]\s[A-Za-z0-9]{5}\s[0-9]{4}\s')
    bn_pattern = re.compile(r'BN:[0-9]+')
    from_ = from_.group()[6:].strip() if from_ is not None else ''
    from_ = re.sub('\n', ' ', from_) if from_ != '' else ''
    from_ = re.sub('\s+', ' ', from_) if from_ != '' else ''
    if from_to_pattern.search(from_) is not None:
        from_airport, from_airline, from_flight_number, from_class, from_date, from_time = from_to_pattern.search(from_).group().strip().split(' ')
    else:
        from_airport, from_airline, from_flight_number, from_class, from_date, from_time = from_[:3], '', '', '', '', ''
    from_bn = bn_pattern.search(from_)
    from_bn = from_bn.group().split(':')[-1] if from_bn is not None else ''
    from_ = ",".join([from_airport, from_airline, from_flight_number, from_class, from_date, from_time, from_bn])
    to_ = to_ if len(to_) > 0 else ''
    if to_ != '':
        to_details = []
        for per_to in to_:
            per_to = per_to[6:-3].strip()
            per_to = re.sub('\n', ' ', per_to)
            per_to = re.sub('\s+', ' ', per_to)
            if from_to_pattern.search(per_to) is not None:
                to_airport, to_airline, to_flight_number, to_class, to_date, to_time = from_to_pattern.search(per_to).group().strip().split(' ')
            else:
                to_airport, to_airline, to_flight_number, to_class, to_date, to_time = per_to[:3], '', '', '', '', ''
            to_bn = bn_pattern.search(per_to)
            to_bn = to_bn.group().split(':')[-1] if to_bn is not None else ''
            to_details.append(','.join([to_airport, to_airline, to_flight_number, to_class, to_date, to_time, to_bn]))
        to_ = ";".join(to_details)
    fare = fare.group().rstrip('|').split(':')[-1].strip() if fare is not None else ''
    tax = tax[-1].rstrip('|').split(':')[-1].strip() if len(tax) > 0 else ''
    total = total.group().rstrip('|').split(':')[-1].strip() if total is not None else ''
    unstructured_data = {
        'issued': issued, 'org': org, 'dst': dst, 'e_r': e_r, 'tour_code': tour_code, 'last_name': last_name,
        'first_name': first_name, 'exch': exch, 'conj': conj, 'from_': from_, 'to_': to_, 'fare': fare, 'tax': tax,
        'total': total, 'date': date,
    }
    return unstructured_data


if __name__ == "__main__":
    pass
