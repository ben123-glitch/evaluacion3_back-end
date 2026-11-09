def canasta_counter(request):
    canasta = request.session.get('canasta', {})
    total_items = sum(item.get('cantidad', 1) for item in canasta.values())
    return {'canasta_count': total_items}
