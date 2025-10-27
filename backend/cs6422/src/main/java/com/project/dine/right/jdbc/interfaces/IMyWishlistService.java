package com.project.dine.right.jdbc.interfaces;

import com.project.dine.right.jdbc.models.MyWishlist;

import java.util.List;

public interface IMyWishlistService {

    List<MyWishlist> findByUserId(Long userId);

}
